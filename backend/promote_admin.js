const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load env vars
dotenv.config({ path: path.join(__dirname, '.env') });

const MONGODB_URI = process.env.MONGODB_URI || "mongodb://127.0.0.1:27017/edumind";

const userSchema = new mongoose.Schema({
    email: String,
    role: String
});

const User = mongoose.model('User', userSchema);

const promoteUser = async (email) => {
    try {
        await mongoose.connect(MONGODB_URI);
        console.log("Connected to MongoDB...");

        const result = await User.updateOne(
            { email: email.trim() },
            { $set: { role: 'admin' } }
        );

        if (result.matchedCount > 0) {
            console.log(`✅ Success! User ${email} is now an ADMIN.`);
            console.log("Please logout and log back in to see the changes.");
        } else {
            console.log(`❌ User with email '${email}' not found.`);
        }
    } catch (err) {
        console.error("❌ Error:", err.message);
    } finally {
        await mongoose.disconnect();
    }
};

const email = process.argv[2];
if (!email) {
    console.log("Please provide an email address.");
    console.log("Usage: node promote_admin.js your-email@example.com");
    process.exit(1);
}

promoteUser(email);
