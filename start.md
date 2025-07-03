# 1. Start your server (this automatically loads your enhanced_agent_with_security.py)
python enhanced_fastapi_server.py

# 2. In another terminal, inject test data
python initial_data.py

# 3. Test it works
curl http://localhost:8000/stats


# 1. Start your enhanced server
python enhanced_fastapi_server.py

# 2. In another terminal, inject test data  
python initial_data.py

# 3. Test comprehensive security audit
curl -X POST http://localhost:8000/security-audit \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/AMRITESH240304/AgentMint"}'

# 4. Test URL cleaning
curl -X POST http://localhost:8000/clean-urls \
  -H "Content-Type: application/json" \
  -d '{"url_text": "Check out github.com/user/repo and https://twitter.com/user"}'