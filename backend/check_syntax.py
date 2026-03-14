try:
    from app.routes import report
    print("Syntax OK")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
