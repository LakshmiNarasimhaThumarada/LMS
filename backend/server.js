const express = require('express'); const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());

// Disable command buffering (fail fast if DB is disconnected)
mongoose.set('bufferCommands', false);

// Ensure uploads directory exists
const uploadDir = 'uploads/';
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// Multer Storage Configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ storage: storage });

// MongoDB Connection with timeout options
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/edumind';

const connectDB = async () => {
    console.log('Attempting to connect to MongoDB...');
    try {
        await mongoose.connect(MONGODB_URI, {
            serverSelectionTimeoutMS: 5000,
            heartbeatFrequencyMS: 2000,
        });
        console.log('Connected to MongoDB Successfully');
    } catch (err) {
        console.error('MongoDB connection error:', err.message);
        throw err; // Propagate the error to prevent server startup
    }
};

// User Schema
const userSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    role: { type: String, enum: ['student', 'admin'], default: 'student' },
    isRestricted: { type: Boolean, default: false },
    unlockedFeatures: { type: [String], default: [] }
});

const User = mongoose.model('User', userSchema);

// Auth Routes
app.post('/api/auth/signup', async (req, res) => {
    try {
        const { name, email, password } = req.body;

        // Check if user exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ message: 'Email already exists' });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create user
        const user = new User({
            name,
            email,
            password: hashedPassword,
            role: 'student'
        });

        await user.save();

        // Generate JWT
        const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || 'secret_key', { expiresIn: '1d' });

        res.status(201).json({
            token,
            user: {
                id: user._id,
                name: user.name,
                email: user.email,
                role: user.role,
                isRestricted: user.isRestricted,
                unlockedFeatures: user.unlockedFeatures
            }
        });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
});

app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        const user = await User.findOne({ email });
        if (!user) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ id: user._id, role: user.role }, process.env.JWT_SECRET || 'secret_key', { expiresIn: '1d' });

        res.json({
            token,
            user: {
                id: user._id,
                name: user.name,
                email: user.email,
                role: user.role,
                isRestricted: user.isRestricted,
                unlockedFeatures: user.unlockedFeatures
            }
        });
    } catch (err) {
        res.status(500).json({ message: 'Server error', error: err.message });
    }
});

const PORT = process.env.PORT || 6000;

// PDF Schema
const pdfSchema = new mongoose.Schema({
    filename: { type: String, required: true },
    uploadDate: { type: Date, default: Date.now },
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true }
});

const PDF = mongoose.model('PDF', pdfSchema);

// Quiz Schema (for stats)
const quizSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    topic: String,
    score: Number,
    date: { type: Date, default: Date.now }
});

const Quiz = mongoose.model('Quiz', quizSchema);

// Quiz Session Schema (Ephemeral storage for a quiz being taken)
const quizSessionSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    pdfId: { type: mongoose.Schema.Types.ObjectId, ref: 'PDF' },
    questions: [{
        question: String,
        options: [String], // Empty for short-answer
        type: { type: String, enum: ['mcq', 'short'] },
        correctAnswer: String,
        explanation: String
    }],
    difficulty: String,
    createdAt: { type: Date, default: Date.now, expires: 3600 } // Auto-delete after 1 hour
});

const QuizSession = mongoose.model('QuizSession', quizSessionSchema);

// Auth Middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.sendStatus(401);

    jwt.verify(token, process.env.JWT_SECRET || 'secret_key', (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
};

const isAdmin = (req, res, next) => {
    if (req.user && req.user.role === 'admin') {
        next();
    } else {
        res.status(403).json({ message: "Access denied. Admin role required." });
    }
};

// Health Check
app.get('/health', (req, res) => res.send('Backend is running'));

// DB Diagnostic Endpoint
app.get('/api/debug/db', (req, res) => {
    const state = mongoose.connection.readyState;
    const states = {
        0: 'disconnected',
        1: 'connected',
        2: 'connecting',
        3: 'disconnecting',
        99: 'uninitialized',
    };

    res.json({
        status: states[state] || 'unknown',
        readyState: state,
        mongodb_uri: MONGODB_URI.replace(/:([^:@]{1,})@/, ':****@'), // Mask password if present
        dbName: mongoose.connection.name
    });
});

// Student Dashboard Routes
app.get('/api/student/stats', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const pdfCount = await PDF.countDocuments({ userId });
        const quizCount = await Quiz.countDocuments({ userId });
        // Mock topics count for now
        const topicsCount = pdfCount * 2;

        res.json({
            pdfs: pdfCount,
            topics: topicsCount,
            quizzes: quizCount
        });
    } catch (err) {
        res.status(500).json({ message: 'Error fetching stats', error: err.message });
    }
});

app.get('/api/student/pdfs', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const pdfs = await PDF.find({ userId }).sort({ uploadDate: -1 });
        res.json(pdfs.map(p => ({
            id: p._id,
            filename: p.filename,
            upload_date: p.uploadDate.toISOString().split('T')[0]
        })));
    } catch (err) {
        res.status(500).json({ message: 'Error fetching PDFs', error: err.message });
    }
});

// PDF Upload Endpoint
app.post('/api/pdf/upload', authenticateToken, upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'No file uploaded' });
        }

        const pdf = new PDF({
            filename: req.file.originalname,
            userId: req.user.id,
            uploadDate: new Date()
        });

        await pdf.save();

        res.status(201).json({
            pdf_id: pdf._id,
            filename: pdf.filename,
            status: "processed"
        });
    } catch (err) {
        res.status(500).json({ message: 'Error uploading PDF', error: err.message });
    }
});

// Chat Endpoint (Mock AI response)
app.post('/api/chat', authenticateToken, async (req, res) => {
    try {
        const { pdf_id, message, conversation_history } = req.body;

        // Simulating Tutor Agent logic
        const response = `Hello! I see you're asking about the PDF (ID: ${pdf_id}). 
        
As your AI tutor, I've analyzed your question: "${message}". 

Based on the content of the document, I can explain that this topic focuses on key concepts and their applications. Would you like me to dive deeper into any specific section or should we try a quick practice problem?`;

        res.json({
            response,
            agent_used: "tutor"
        });
    } catch (err) {
        res.status(500).json({ message: 'Error in chat', error: err.message });
    }
});

// --- Quiz Endpoints ---

// Generate Quiz (Mock Logic)
app.post('/api/quiz/generate', authenticateToken, async (req, res) => {
    try {
        const { pdf_id, num_questions = 5, difficulty = 'medium' } = req.body;

        // Simulating Quiz Agent via LangGraph
        // In a real app, you would fetch PDF content and use an LLM
        const mockQuestions = [
            {
                question: "What is the primary theme discussed in the document?",
                options: ["Option A", "Option B", "Option C", "Option D"],
                type: "mcq",
                correctAnswer: "Option A",
                explanation: "The document focuses on Option A as its foundation."
            },
            {
                question: "Which of the following is a key requirement mentioned?",
                options: ["Fast speed", "Low cost", "High security", "Scalability"],
                type: "mcq",
                correctAnswer: "Scalability",
                explanation: "Scalability is highlighted in the introduction."
            },
            {
                question: "According to the text, why is the 'LLM-as-Judge' pattern used?",
                options: ["Automation", "Cost saving", "Evaluating non-deterministic outputs", "Speed"],
                type: "mcq",
                correctAnswer: "Evaluating non-deterministic outputs",
                explanation: "LLM-as-Judge is perfect for evaluating open-ended answers."
            },
            {
                question: "Briefly explain the main objective of the proposed system.",
                type: "short",
                correctAnswer: "To provide automated tutoring and evaluation.",
                explanation: "The system aims to use AI to assist students in learning."
            },
            {
                question: "What are the three main components of the architecture?",
                type: "short",
                correctAnswer: "Frontend, Backend, and AI Service.",
                explanation: "These three layers form the core infrastructure."
            }
        ];

        const session = new QuizSession({
            userId: req.user.id,
            pdfId: pdf_id,
            questions: mockQuestions.slice(0, num_questions),
            difficulty
        });

        await session.save();

        res.status(201).json({
            quiz_id: session._id,
            questions: session.questions.map(q => ({
                id: q._id,
                question: q.question,
                options: q.options,
                type: q.type
            }))
        });
    } catch (err) {
        res.status(500).json({ message: 'Error generating quiz', error: err.message });
    }
});

// Evaluate Quiz (LLM-as-Judge Mock)
app.post('/api/quiz/evaluate', authenticateToken, async (req, res) => {
    try {
        const { quiz_id, answers } = req.body;
        const session = await QuizSession.findById(quiz_id);
        if (!session) return res.status(404).json({ message: "Quiz session not found" });

        let score = 0;
        const results = session.questions.map((q, index) => {
            const userAnswer = answers[index];
            let isCorrect = false;

            if (q.type === 'mcq') {
                isCorrect = userAnswer === q.correctAnswer;
            } else {
                // LLM-as-Judge Mock Logic
                // In reality, you'd prompt: 'Is this answer correct? Explain why or why not.'
                isCorrect = userAnswer.length > 10; // Simple heuristic for mock
            }

            if (isCorrect) score++;

            return {
                question: q.question,
                user_answer: userAnswer,
                correct_answer: q.correctAnswer,
                is_correct: isCorrect,
                explanation: q.explanation
            };
        });

        res.json({
            score: `${score}/${session.questions.length}`,
            percentage: (score / session.questions.length) * 100,
            results
        });
    } catch (err) {
        res.status(500).json({ message: 'Error evaluating quiz', error: err.message });
    }
});

// Save Result
app.post('/api/quiz/save-result', authenticateToken, async (req, res) => {
    try {
        const { quiz_id, score, topic } = req.body;
        // score is expected as "4/5" string
        const numericScore = parseInt(score.split('/')[0]) || 0;

        const quizResult = new Quiz({
            userId: req.user.id,
            topic: topic || "General Quiz",
            score: numericScore,
            date: new Date()
        });

        await quizResult.save();
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ message: 'Error saving result', error: err.message });
    }
});

// --- Progress Tracking Endpoints ---

// Get Overall Progress (KPIs)
app.get('/api/student/progress', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const quizzes = await Quiz.find({ userId });

        // Mock calculations for demo purposes
        const totalHours = quizzes.length * 1.5; // Simple heuristic
        const avgScore = quizzes.length > 0 ?
            (quizzes.reduce((acc, q) => acc + q.score, 0) / quizzes.length) : 0;

        // Mock streak calculation
        const streak = quizzes.length > 0 ? 5 : 0;

        res.json({
            study_hours: parseFloat(totalHours.toFixed(1)),
            streak: streak,
            avg_score: parseFloat((avgScore * 20).toFixed(1)) // Assuming score is out of 5, convert to %
        });
    } catch (err) {
        res.status(500).json({ message: 'Error fetching progress', error: err.message });
    }
});

// Get Quiz History (for Line Chart)
app.get('/api/student/quiz-history', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const quizzes = await Quiz.find({ userId }).sort({ date: 1 });

        res.json(quizzes.map(q => ({
            date: q.date.toISOString().split('T')[0],
            score: q.score * 20, // Convert to %
            topic: q.topic
        })));
    } catch (err) {
        res.status(500).json({ message: 'Error fetching quiz history', error: err.message });
    }
});

// Get Topic-wise scores (for Bar Chart)
app.get('/api/student/topic-scores', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const topicData = await Quiz.aggregate([
            { $match: { userId: new mongoose.Types.ObjectId(userId) } },
            { $group: { _id: "$topic", avgScore: { $avg: "$score" } } }
        ]);

        res.json(topicData.map(t => ({
            topic: t._id,
            avg_score: parseFloat((t.avgScore * 20).toFixed(1))
        })));
    } catch (err) {
        res.status(500).json({ message: 'Error fetching topic scores', error: err.message });
    }
});

// Get AI Recommendations
app.post('/api/student/get-recommendations', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const weakTopics = await Quiz.aggregate([
            { $match: { userId: new mongoose.Types.ObjectId(userId) } },
            { $group: { _id: "$topic", avgScore: { $avg: "$score" } } },
            { $match: { avgScore: { $lt: 3.5 } } } // Less than 70%
        ]);

        const recommendations = weakTopics.map(t =>
            `You should review ${t._id} — you scored ${(t.avgScore * 20).toFixed(0)}% on the last quiz.`
        );

        if (recommendations.length === 0) {
            recommendations.push("Great job! You're performing well across all topics. Consider exploring new advanced materials.");
        }

        res.json({ recommendations });
    } catch (err) {
        res.status(500).json({ message: 'Error getting recommendations', error: err.message });
    }
});

// --- Admin Endpoints ---

// Get System Stats
app.get('/api/admin/stats', authenticateToken, isAdmin, async (req, res) => {
    try {
        const studentCount = await User.countDocuments({ role: 'student' });
        const pdfCount = await PDF.countDocuments();
        const quizCount = await Quiz.countDocuments();

        res.json({
            total_students: studentCount,
            total_pdfs: pdfCount,
            total_quizzes: quizCount
        });
    } catch (err) {
        res.status(500).json({ message: 'Error fetching admin stats', error: err.message });
    }
});

// Get All Students with Summary
app.get('/api/admin/students', authenticateToken, isAdmin, async (req, res) => {
    try {
        const students = await User.find({ role: 'student' }).select('-password');

        const studentData = await Promise.all(students.map(async (s) => {
            const quizCount = await Quiz.countDocuments({ userId: s._id });
            const avgScoreData = await Quiz.aggregate([
                { $match: { userId: s._id } },
                { $group: { _id: null, avg: { $avg: "$score" } } }
            ]);

            return {
                id: s._id,
                name: s.name,
                email: s.email,
                join_date: s._id.getTimestamp().toISOString().split('T')[0],
                last_active: "Today", // Simplified
                quiz_count: quizCount,
                avg_score: avgScoreData.length > 0 ? (avgScoreData[0].avg * 20).toFixed(1) : "0"
            };
        }));

        res.json(studentData);
    } catch (err) {
        res.status(500).json({ message: 'Error fetching students', error: err.message });
    }
});

// Get Detailed Student Info
app.get('/api/admin/student/:id', authenticateToken, isAdmin, async (req, res) => {
    try {
        const userId = req.params.id;
        const user = await User.findById(userId).select('-password');
        if (!user) return res.status(404).json({ message: "Student not found" });

        const pdfs = await PDF.find({ userId });
        const quizzes = await Quiz.find({ userId }).sort({ date: -1 });

        const topicScores = await Quiz.aggregate([
            { $match: { userId: new mongoose.Types.ObjectId(userId) } },
            { $group: { _id: "$topic", avgScore: { $avg: "$score" } } }
        ]);

        res.json({
            user,
            pdfs: pdfs.map(p => ({ filename: p.filename, date: p.uploadDate })),
            quizzes: quizzes.map(q => ({ topic: q.topic, score: q.score * 20, date: q.date })),
            weak_topics: topicScores.filter(t => t.avgScore < 3.5).map(t => t._id)
        });
    } catch (err) {
        res.status(500).json({ message: 'Error fetching student details', error: err.message });
    }
});

// Update Student (Restrict/Unlock)
app.patch('/api/admin/student/:id', authenticateToken, isAdmin, async (req, res) => {
    try {
        const { isRestricted, unlockedFeatures } = req.body;
        const updateData = {};
        if (isRestricted !== undefined) updateData.isRestricted = isRestricted;
        if (unlockedFeatures !== undefined) updateData.unlockedFeatures = unlockedFeatures;

        const user = await User.findByIdAndUpdate(req.params.id, updateData, { new: true }).select('-password');
        if (!user) return res.status(404).json({ message: "Student not found" });

        res.json({ success: true, user });
    } catch (err) {
        res.status(500).json({ message: 'Error updating student', error: err.message });
    }
});

// Delete Student
app.delete('/api/admin/student/:id', authenticateToken, isAdmin, async (req, res) => {
    try {
        const userId = req.params.id;
        await User.findByIdAndDelete(userId);
        // Cascading delete for other data
        await PDF.deleteMany({ userId });
        await Quiz.deleteMany({ userId });
        await QuizSession.deleteMany({ userId });

        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ message: 'Error deleting student', error: err.message });
    }
});

// Server Startup Logic
const startServer = async () => {
    try {
        console.log('Starting EduMind Backend...');

        // Ensure uploads directory exists
        const uploadDir = 'uploads/';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir);
            console.log('Created missing uploads directory');
        }

        // Try to connect to MongoDB first
        await connectDB();

        // Only start listening if DB connection didn't throw
        app.listen(PORT, () => {
            console.log(`Server is listening on 127.0.0.1:${PORT}`);
            console.log('Ready to handle requests ✨');
        });
    } catch (err) {
        console.error('CRITICAL: Failed to start server:', err.message);
        console.log('\n💡 Tip: If this is a connection error, make sure MongoDB is running.');
        console.log('Try running "net start MongoDB" in an Administrator Command Prompt.\n');
        process.exit(1);
    }
};

startServer();
