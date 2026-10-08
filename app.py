# --- AUTO-RETRY LOOP & 2.0-FLASH MODEL ---
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.0-flash', # Switched to 2.0-flash for high free limits!
                        contents=final_prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type='application/json',
                        ),
                    )
                    break 
                except Exception as api_e:
                    if "503" in str(api_e) and attempt < max_retries - 1:
                        time.sleep(5) 
                        continue
                    else:
                        raise api_e 
            # --------------------------------
