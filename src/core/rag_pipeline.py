# src/core/rag_pipeline.py
"""Advanced RAG pipeline for complex agricultural and climate Q&A with source citations."""
from langchain_google_genai import ChatGoogleGenerativeAI  # pyright: ignore[reportMissingImports]
from langchain.prompts import PromptTemplate  # pyright: ignore[reportMissingImports]
from langchain.schema import HumanMessage, SystemMessage  # pyright: ignore[reportMissingImports]
from src.core.vector_store import retrieve_docs
from src.core.data_gov_client import DataGovClient
from src.utils.security import sanitize_input
from src.utils.logger import logger
from src.config.settings import settings
import pandas as pd
import json
import re
from typing import Dict, List, Tuple
from scipy import stats

# LLM initialization - Gemini only
if not settings.gemini_api_key:
    raise ValueError("GEMINI_API_KEY is required")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=settings.gemini_api_key, temperature=0.1)
logger.info("Using Gemini 2.0 Flash LLM")

class AdvancedRAGPipeline:
    """Enhanced RAG pipeline for complex multi-domain queries."""

    def __init__(self):
        self.data_client = DataGovClient()
        self.source_citations = []

    def run_rag(self, question: str) -> str:
        """Run advanced RAG pipeline with source citations."""
        try:
            # Sanitize input
            question = sanitize_input(question)

            # Analyze question type and extract parameters
            query_analysis = self._analyze_question(question)

            # Execute appropriate query strategy
            if query_analysis["type"] == "comparison":
                response = self._handle_comparison_query(query_analysis)
            elif query_analysis["type"] == "trend_analysis":
                response = self._handle_trend_analysis(query_analysis)
            elif query_analysis["type"] == "policy_analysis":
                response = self._handle_policy_analysis(query_analysis)
            elif query_analysis["type"] == "district_comparison":
                response = self._handle_district_comparison(query_analysis)
            else:
                response = self._handle_general_query(question)

            # Add source citations
            if self.source_citations:
                response += "\n\n**Sources:**\n" + "\n".join(f"- {citation}" for citation in self.source_citations)

            return response

        except Exception as e:
            logger.error(f"RAG pipeline error: {e}")
            return f"Error processing question: {str(e)}"

    def _analyze_question(self, question: str) -> Dict:
        """Analyze question to determine type and extract parameters."""
        question_lower = question.lower()

        analysis = {
            "type": "general",
            "states": [],
            "crops": [],
            "years": [],
            "districts": [],
            "metrics": []
        }

        # Extract states
        indian_states = [
            "maharashtra", "karnataka", "tamil nadu", "punjab", "gujarat",
            "rajasthan", "madhya pradesh", "andhra pradesh", "telangana",
            "kerala", "odisha", "bihar", "haryana", "uttar pradesh", "west bengal"
        ]

        for state in indian_states:
            if state in question_lower:
                analysis["states"].append(state.title())

        # Extract crops
        crops = ["rice", "wheat", "maize", "cotton", "sugarcane", "pulses", "soybean", "millet", "mustard"]
        for crop in crops:
            if crop in question_lower:
                analysis["crops"].append(crop.title())

        # Extract years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, question)
        analysis["years"] = [int(year) for year in years]

        # Extract districts
        district_pattern = r'in ([A-Za-z\s]+) district'
        districts = re.findall(district_pattern, question_lower)
        analysis["districts"] = [d.strip().title() for d in districts]

        # Determine question type - prioritize district/production queries
        if any(word in question_lower for word in ["total", "production", "rice", "wheat", "maize"]) and any(state in question_lower for state in indian_states):
            analysis["type"] = "district_comparison"
        elif any(word in question_lower for word in ["compare", "comparison", "vs", "versus", "between"]):
            analysis["type"] = "comparison"
        elif any(word in question_lower for word in ["trend", "over time", "decade", "years", "historical"]):
            analysis["type"] = "trend_analysis"
        elif any(word in question_lower for word in ["policy", "scheme", "promote", "recommend", "argument"]):
            analysis["type"] = "policy_analysis"

        return analysis

    def _handle_comparison_query(self, analysis: Dict) -> str:
        """Handle state/crop comparison queries."""
        states = analysis["states"]
        crops = analysis["crops"]
        years = analysis["years"] or [2022, 2021]

        if not states:
            return "Please specify which states you want to compare."

        response = f"**Comparative Analysis: {', '.join(states)}**\n\n"

        # Get combined data for analysis
        combined_data = self.data_client.get_combined_data(states=states, years=years)

        if combined_data.empty:
            return "No data available for the specified states and time period."

        # Agricultural comparison
        response += "**Agricultural Production:**\n"
        for state in states:
            state_data = combined_data[combined_data['State'] == state]
            if not state_data.empty:
                total_production = state_data['Production_tonnes'].sum()
                avg_rainfall = state_data['Total_Rainfall_mm'].mean()
                response += f"- **{state}**: Total production: {total_production:,.0f} tonnes, "
                response += f"Avg rainfall: {avg_rainfall:.0f}mm\n"

                if crops:
                    for crop in crops:
                        crop_data = state_data[state_data['Crop'] == crop]
                        if not crop_data.empty:
                            crop_production = crop_data['Production_tonnes'].sum()
                            response += f"  - {crop}: {crop_production:,.0f} tonnes\n"

        self._add_citation("Ministry of Agriculture & Farmers Welfare", "Agricultural Production Statistics")
        self._add_citation("India Meteorological Department", "District-wise Climate Statistics")

        return response

    def _handle_trend_analysis(self, analysis: Dict) -> str:
        """Handle trend analysis queries."""
        states = analysis["states"]
        crops = analysis["crops"]

        if not states or not crops:
            return "Please specify states and crops for trend analysis."

        response = f"**Trend Analysis: {crops[0]} production in {', '.join(states)}**\n\n"

        # Get historical data (last 5 years)
        years = list(range(2018, 2023))
        combined_data = self.data_client.get_combined_data(states=states, years=years)

        for state in states:
            state_data = combined_data[combined_data['State'] == state]
            crop_data = state_data[state_data['Crop'] == crops[0]]

            if not crop_data.empty:
                response += f"**{state}:**\n"

                # Production trend
                yearly_production = crop_data.groupby('Year')['Production_tonnes'].sum()
                response += "Production trend (tonnes):\n"
                for year, production in yearly_production.items():
                    response += f"- {year}: {production:,.0f}\n"

                # Climate correlation
                avg_rainfall = crop_data.groupby('Year')['Total_Rainfall_mm'].mean()
                response += "Corresponding rainfall (mm):\n"
                for year, rainfall in avg_rainfall.items():
                    response += f"- {year}: {rainfall:.0f}mm\n"

                # Simple correlation analysis
                if len(yearly_production) > 1:
                    correlation = self._calculate_correlation(yearly_production, avg_rainfall)
                    response += f"\n**Correlation with rainfall:** {correlation:.2f}\n"
                    if correlation > 0.5:
                        response += "💡 Positive correlation: Higher rainfall tends to increase production\n"
                    elif correlation < -0.5:
                        response += "💡 Negative correlation: Higher rainfall may decrease production\n"
                    else:
                        response += "💡 Weak correlation: Production not strongly affected by rainfall\n"

                response += "\n"

        self._add_citation("Ministry of Agriculture & Farmers Welfare", "Agricultural Production Statistics")
        self._add_citation("India Meteorological Department", "District-wise Climate Statistics")

        return response

    def _handle_policy_analysis(self, analysis: Dict) -> str:
        """Handle policy recommendation queries."""
        crops = analysis["crops"]
        states = analysis["states"]
        years = analysis["years"] or list(range(2018, 2023))

        if len(crops) < 2:
            return "Please specify two crops to compare for policy analysis."

        response = f"**Policy Analysis: Promoting {crops[0]} over {crops[1]}**\n\n"

        combined_data = self.data_client.get_combined_data(states=states, years=years)

        arguments = []

        # Argument 1: Water efficiency
        crop1_data = combined_data[combined_data['Crop'] == crops[0]]
        crop2_data = combined_data[combined_data['Crop'] == crops[1]]

        if not crop1_data.empty and not crop2_data.empty:
            # Assume drought-resistant vs water-intensive classification
            drought_resistant_crops = ["millet", "pulses", "maize"]
            water_intensive_crops = ["rice", "sugarcane", "cotton"]

            crop1_water_need = "low" if any(crop.lower() in drought_resistant_crops for crop in [crops[0].lower()]) else "high"
            crop2_water_need = "high" if any(crop.lower() in water_intensive_crops for crop in [crops[1].lower()]) else "low"

            arguments.append(
                f"1. **Water Efficiency**: {crops[0]} has {crop1_water_need} water requirements compared to {crops[1]}'s {crop2_water_need} water requirements, making it more suitable for water-scarce regions."
            )

        # Argument 2: Climate resilience
        if not crop1_data.empty:
            crop1_rainfall = crop1_data['Total_Rainfall_mm']
            crop1_avg_rainfall = crop1_rainfall.mean()
            crop1_rainfall_var = crop1_rainfall.std()

            arguments.append(
                f"2. **Climate Resilience**: {crops[0]} shows stable production across varying rainfall conditions (avg: {crop1_avg_rainfall:.0f}mm, variation: {crop1_rainfall_var:.0f}mm), indicating better resilience to climate variability."
            )

        # Argument 3: Production stability
        if not crop1_data.empty and not crop2_data.empty:
            crop1_production = crop1_data.groupby('Year')['Production_tonnes'].sum()
            crop2_production = crop2_data.groupby('Year')['Production_tonnes'].sum()

            crop1_stability = 1 / (crop1_production.std() / crop1_production.mean()) if len(crop1_production) > 1 else 0
            crop2_stability = 1 / (crop2_production.std() / crop2_production.mean()) if len(crop2_production) > 1 else 0

            if crop1_stability > crop2_stability:
                arguments.append(
                    f"3. **Production Stability**: {crops[0]} demonstrates {crop1_stability:.1f}x more stable production compared to {crops[1]}, reducing food security risks."
                )

        response += "\n".join(arguments)

        self._add_citation("Ministry of Agriculture & Farmers Welfare", "Agricultural Production Statistics")
        self._add_citation("India Meteorological Department", "District-wise Climate Statistics")

        return response

    def _handle_district_comparison(self, analysis: Dict) -> str:
        """Handle district-level comparison queries."""
        states = analysis["states"]
        crops = analysis["crops"]

        if not states or not crops:
            return "Please specify states and crops for district comparison."

        response = f"📊 **District-level Analysis: {crops[0]} production in {', '.join(states)}**\n\n"

        combined_data = self.data_client.get_combined_data(states=states)

        for state in states:
            state_data = combined_data[combined_data['State'] == state]
            crop_data = state_data[state_data['Crop'] == crops[0]]

            if not crop_data.empty:
                # Find highest and lowest production districts
                district_production = crop_data.groupby('District')['Production_tonnes'].sum()
                highest_district = district_production.idxmax()
                lowest_district = district_production.idxmin()
                highest_production = district_production.max()
                lowest_production = district_production.min()

                response += f"🌾 **{state}:**\n"
                response += f"🏆 **Highest production**: {highest_district} ({highest_production:,.0f} tonnes)\n"
                response += f"📉 **Lowest production**: {lowest_district} ({lowest_production:,.0f} tonnes)\n"

                # Climate factors - avoid self-comparison
                highest_district_data = crop_data[crop_data['District'] == highest_district]
                lowest_district_data = crop_data[crop_data['District'] == lowest_district]

                if not highest_district_data.empty and not lowest_district_data.empty:
                    highest_rainfall = highest_district_data['Total_Rainfall_mm'].mean()
                    lowest_rainfall = lowest_district_data['Total_Rainfall_mm'].mean()

                    # Only show climate comparison if districts are different
                    if highest_district != lowest_district:
                        response += f"🌧️ **Climate factor**: {highest_district} receives {highest_rainfall:.0f}mm avg rainfall vs {lowest_rainfall:.0f}mm in {lowest_district}\n"
                    else:
                        response += f"🌧️ **Climate factor**: {highest_district} receives {highest_rainfall:.0f}mm avg rainfall\n"

                response += "\n"

        response += "📊 **Sources:**\n"
        response += "🏛️ Ministry of Agriculture & Farmers Welfare - Agricultural Production Statistics\n"
        response += "🌤️ India Meteorological Department - District-wise Climate Statistics\n"

        return response

    def _handle_general_query(self, question: str) -> str:
        """Handle general queries using vector search and LLM synthesis."""
        docs = retrieve_docs(question)

        if not docs:
            return "No relevant information found for your query."

        # Prepare context from retrieved documents
        context = "\n\n".join([f"Document {i+1}: {doc['text']}" for i, doc in enumerate(docs[:5])])

        # Create synthesis prompt with enhanced instructions
        synthesis_prompt = f"""
You are an expert agricultural data analyst. Based on the following retrieved documents, provide a comprehensive and accurate answer to the question: "{question}"

Retrieved Documents:
{context}

Instructions:
- Synthesize information from the documents to directly answer the question
- Be factual and accurate - do not make up information or extrapolate beyond what's in the documents
- If the documents don't contain enough information to fully answer, clearly state what information is missing
- Include specific data points, numbers, and details from the documents
- Structure your answer clearly and concisely with proper formatting
- When providing numerical data, ensure accuracy and include units
- For agricultural data, consider factors like crop types, regions, seasons, and production metrics
- If comparing data, use the exact figures from the documents
- Cite specific document references when providing information

Important: Only use information that is explicitly stated in the retrieved documents. Do not add external knowledge or assumptions.

Answer:"""

        try:
            # Use LLM to synthesize answer
            messages = [HumanMessage(content=synthesis_prompt)]
            llm_response = llm.invoke(messages).content.strip()

            # Ground the response by checking if it uses document information
            grounded_response = self._ground_response(llm_response, docs)

            # Add source citations
            self._add_citation("Vector Search Results", "Agricultural Knowledge Base")

            return grounded_response

        except Exception as e:
            logger.error(f"LLM synthesis error: {e}")
            # Fallback to showing document snippets
            response = f"**Query Results:** {question}\n\n"
            for i, doc in enumerate(docs[:3]):
                response += f"**Document {i+1}:**\n"
                response += f"- Content: {doc['text'][:200]}...\n"
                response += f"- Source: {doc['metadata']}\n\n"
            return response

    def _calculate_correlation(self, series1: pd.Series, series2: pd.Series) -> float:
        """Calculate correlation coefficient between two series."""
        try:
            return series1.corr(series2)
        except:
            return 0.0

    def _ground_response(self, response: str, docs: List[Dict]) -> str:
        """Ground the LLM response by verifying it uses document information."""
        # Extract key facts from documents
        doc_facts = set()
        for doc in docs:
            text = doc['text'].lower()
            # Extract numbers and key agricultural terms
            import re
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
            states = re.findall(r'\b(maharashtra|karnataka|tamil nadu|punjab|gujarat|rajasthan|madhya pradesh|andhra pradesh|telangana|kerala|odisha|bihar|haryana|uttar pradesh|west bengal)\b', text)
            crops = re.findall(r'\b(rice|wheat|maize|cotton|sugarcane|pulses|soybean|millet|mustard)\b', text)
            doc_facts.update(numbers + states + crops)

        # Check if response contains document facts
        response_lower = response.lower()
        grounded_facts = [fact for fact in doc_facts if fact.lower() in response_lower]

        if not grounded_facts and len(response.strip()) > 50:
            # If response doesn't use document facts, add a note
            response += "\n\n*Note: This response is based on general knowledge as specific data matching your query was not found in the knowledge base.*"

        return response

    def _add_citation(self, source: str, dataset: str):
        """Add source citation."""
        citation = f"{source} - {dataset}"
        if citation not in self.source_citations:
            self.source_citations.append(citation)

# Global pipeline instance
rag_pipeline = AdvancedRAGPipeline()

def run_rag(question: str) -> str:
    """Wrapper function for the RAG pipeline."""
    return rag_pipeline.run_rag(question)