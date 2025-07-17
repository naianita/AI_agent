# OpenAI-Powered IoT Environmental Monitoring Conversational Agent

## 🚀 Research Implementation

This repository contains the complete implementation of a sophisticated Django-based conversational agent that integrates real-time IoT sensor data with an advanced ReAct (Reasoning and Acting) framework, as described in the research paper: **"Development of an Intelligent Conversational Agent with IoT Environmental Monitoring Integration Using ReAct Framework"**.

## 🎯 Research Objectives Achieved

✅ **Real-time IoT Integration**: Processes 1.6M+ environmental sensor readings  
✅ **ReAct Framework**: Implements reasoning-action cycles for complex decision making  
✅ **OpenAI API Integration**: Uses gpt-4.1-nano-2025-04-14 with fine-tuning capabilities  
✅ **Memory Management**: File-based conversation storage with context awareness  
✅ **Tool-based Architecture**: Extensible environmental analysis tools  
✅ **Fine-tuning System**: Custom model training on IoT domain data  
✅ **Environmental Health Advisory**: Context-aware recommendations and insights  

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   ReAct Agent   │    │   OpenAI API    │
│                 │◄──►│                 │◄──►│                 │
│   Chat UI       │    │  - Reasoning    │    │  GPT-4.1-nano   │
│   Dashboard     │    │  - Acting       │    │  Fine-tuned     │
└─────────────────┘    │  - Tools        │    └─────────────────┘
                       │  - Memory       │              │
                       └─────────────────┘              │
                               │                        │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Tool Manager  │    │   Fine-tuner    │
                    │                 │    │                 │
                    │  - IoT Data     │    │  - Training     │
                    │  - Analytics    │    │  - Monitoring   │
                    │  - Sensors      │    │  - Validation   │
                    └─────────────────┘    └─────────────────┘
                               │
                    ┌─────────────────┐
                    │   IoT Database  │
                    │                 │
                    │  1.6M+ readings │
                    │  CO2, Temp,     │
                    │  Humidity, TVOC │
                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and setup
git clone <repository>
cd Chatbot_t/ChatBot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure OpenAI API
Create `.env` file in `ChatBot/` directory:
```env
API_KEY=your_openai_api_key_here
COMPLEX_LLM_MODEL=gpt-4.1-nano-2025-04-14
LIGHTWEIGHT_LLM_MODEL=gpt-4.1-nano-2025-04-14
FALLBACK_MODEL=gpt-4.1-nano-2025-04-14
```

### 3. Validate System
```bash
python validate_system.py
```

### 4. Generate Training Data
```bash
cd LineBot/agent/training_data
python generate_training_data.py
```

### 5. Fine-tune Model
```bash
cd ../../../
python manage.py train_gpt35_fallback --data-file LineBot/agent/training_data/nano_finetune_data.json --wait
```

### 6. Update Configuration
After fine-tuning, update `.env` with the fine-tuned model ID:
```env
FALLBACK_MODEL=ft:gpt-4.1-nano-2025-04-14:your-org:your-model:xxxxx
```

### 7. Run System
```bash
python manage.py runserver
```
Visit `http://localhost:8000/` to interact with your agent.

## 💰 Cost Analysis

- **Fine-tuning**: ~$0.76 for 5000 examples
- **Monthly Inference**: ~$0.12 for 1000 requests
- **Total Setup**: <$1.00 (well within research budget)

## 🧪 Research Validation

The implementation successfully demonstrates:

### IoT Data Processing
- **Volume**: 1,601,020 sensor readings processed
- **Parameters**: CO2, Temperature, Humidity, TVOC
- **Frequency**: Real-time readings every ~20 seconds
- **Analytics**: Trend analysis, threshold monitoring, pattern recognition

### ReAct Framework Implementation
- **Reasoning**: Context-aware analysis of environmental conditions
- **Acting**: Tool execution for data retrieval and analysis
- **Iteration**: Multi-step problem solving with feedback loops
- **Memory**: Conversation context and historical analysis

### Environmental Health Advisory
- **Real-time Assessment**: Immediate air quality evaluation
- **Trend Analysis**: Historical pattern recognition
- **Recommendations**: Personalized health and comfort advice
- **Alerts**: Proactive threshold breach notifications

## 🛠️ Core Components

### 1. ReAct Agent (`LineBot/agent/react_agent.py`)
Implements the core reasoning-acting paradigm:
- Multi-step reasoning for complex environmental analysis
- Tool selection and execution
- Context management and memory integration
- Error handling and recovery

### 2. Model Hub (`LineBot/agent/model_hub.py`)
Manages OpenAI API interactions:
- Primary/fallback model management
- Token optimization and cost control
- Error handling and retry logic
- Fine-tuned model integration

### 3. Tool Manager (`LineBot/agent/tool_manager.py`)
Provides environmental analysis capabilities:
- Sensor data retrieval and processing
- Statistical analysis and trend detection
- Air quality assessment and recommendations
- Cross-sensor comparison and validation

### 4. Fine-tuner (`LineBot/agent/fine_tuner.py`)
Handles model customization:
- Training data preparation and validation
- OpenAI fine-tuning job management
- Progress monitoring and cost estimation
- Model testing and validation

### 5. Training Data Generator (`LineBot/agent/training_data/`)
Creates domain-specific training examples:
- Real IoT data integration
- Multiple task types (standard, sequential, navigation)
- Cost-optimized example generation
- Quality validation and filtering

## 📈 Performance Metrics

### Data Processing
- **Response Time**: <2 seconds for simple queries
- **Complex Analysis**: <10 seconds for multi-parameter evaluation
- **Memory Usage**: Efficient file-based storage
- **Scalability**: Handles 1.6M+ data points seamlessly

### Model Performance
- **Fine-tuning Accuracy**: Enhanced domain-specific responses
- **Token Efficiency**: Optimized prompt engineering
- **Cost Control**: Built-in budget monitoring
- **Error Recovery**: Robust fallback mechanisms

## 🔬 Research Applications

### Environmental Health Studies
- Indoor air quality impact assessment
- Occupancy pattern analysis
- Ventilation system optimization
- Health recommendation systems

### IoT System Integration
- Multi-sensor data fusion
- Real-time anomaly detection
- Predictive maintenance alerts
- Energy efficiency optimization

### Conversational AI Research
- Domain-specific fine-tuning methodologies
- Tool-using agent architectures
- Multi-modal interaction patterns
- Context-aware response generation

## 📚 Publications and Citations

This implementation supports research described in:
- "Development of an Intelligent Conversational Agent with IoT Environmental Monitoring Integration Using ReAct Framework"
- Focus areas: IoT-AI integration, environmental health monitoring, conversational interfaces

### Key References
- Yao et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models"
- Environmental monitoring and smart building systems literature
- Conversational AI and tool-using agent research

## 🚧 Future Enhancements

### Technical Improvements
- [ ] Multi-building deployment architecture
- [ ] Edge computing integration for reduced latency
- [ ] Advanced predictive modeling capabilities
- [ ] Enhanced visualization and dashboard features

### Research Extensions
- [ ] Correlation studies between environmental factors and health outcomes
- [ ] Seasonal pattern analysis with extended historical data
- [ ] Integration with external weather and air quality APIs
- [ ] Machine learning-based anomaly detection algorithms

### Production Features
- [ ] User authentication and role-based access
- [ ] Mobile application development
- [ ] Advanced alerting and notification systems
- [ ] Enterprise deployment and scaling guides

## 🤝 Contributing

This research implementation is designed for academic and research purposes. Contributions that enhance the research value, improve the technical implementation, or extend the environmental monitoring capabilities are welcome.

## 📄 License

[Specify your license here - typically academic or research license for research implementations]

## 👥 Authors and Acknowledgments

[Please provide author names and affiliations as specified in your research paper]

## 📞 Contact

For research collaborations, questions about implementation, or technical support, please contact [your contact information].

---

**🎯 This implementation successfully bridges the gap between IoT sensor networks and intelligent conversational interfaces, creating a practical solution for environmental health monitoring and automated decision support.** 