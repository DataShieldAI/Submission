# 1. Start your server (this automatically loads your enhanced_agent_with_security.py)
python enhanced_fastapi_server.py

# 2. In another terminal, inject test data
python initialize_contract.py

# 3. Test it works
curl http://localhost:8000/stats