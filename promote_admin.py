import pymongo
import sys

# Connection URL from your .env
MONGO_URI = "mongodb://127.0.0.1:27017/edumind"

def make_admin(email):
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client.edumind
        users = db.users
        
        result = users.update_one(
            {"email": email},
            {"$set": {"role": "admin"}}
        )
        
        if result.matched_count > 0:
            print(f"✅ Success! User {email} is now an ADMIN.")
            print("Please logout and log back in to see the changes.")
        else:
            print(f"❌ User with email '{email}' not found.")
            
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter the email address of the user you want to make admin: ")
    
    make_admin(email.strip())
