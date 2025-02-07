from lounasvahti.services.email_service import receive_email_blocking

def main():
    print("Listening for emails")
    receive_email_blocking()

if __name__ == "__main__":
    main()
