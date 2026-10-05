from services.ai_service import analyze_ticket


result = analyze_ticket(
    "Cannot login",
    "I changed my password yesterday but I still cannot login."
)

print(result)