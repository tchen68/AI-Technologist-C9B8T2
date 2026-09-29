// ============================================================================
// chatbot.jsx - Capacity Planning RAG Chatbot UI (Lab 4)
// Author: Thomas Chen | AI Technologist Course
// ============================================================================

import React, { useState, useRef, useEffect } from 'react';
import {
    Box, TextField, IconButton, Typography, Paper, AppBar, Toolbar,
    CircularProgress, Card, CardContent, Divider, Chip, Alert, Slider,
    Tooltip, Stack, Collapse, Button
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import DeleteSweepIcon from "@mui/icons-material/DeleteSweep";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import DescriptionIcon from "@mui/icons-material/Description";
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';

// Starter prompts set user expectations and keep questions in scope.
// Edit these to match the documents you actually ingested.
const SUGGESTED_PROMPTS = [
    "How is a site name derived from an operator LAN ID?",
    "Which sites roll up to Accenture vs Concentrix?",
    "How do cash allocation tables get their site and vendor?",
    "What data does the GOAT schema provide?",
    "What does the capacity planning spec cover?"
];

const tempHint = (t) => {
    if (t <= 0.3) return "Precise - policy, thresholds, definitions";
    if (t <= 0.6) return "Balanced - explanations and summaries";
    return "Exploratory - brainstorming only, never for numbers";
};

const Chatbot = () => {

    // ========================================================================
    // SECTION 1 - STATE
    // ========================================================================

    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content:
                "Hi Thomas. I'm the Capacity Planning Knowledge Assistant. I answer " +
                "from approved capacity planning documentation and cite the source " +
                "for every answer. If something isn't documented, I'll say so rather " +
                "than guess. Pick a starter question below or ask your own.",
            sources: [],
            grounded: true
        }
    ]);

    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [temperature, setTemperature] = useState(0.2);
    const [health, setHealth] = useState(null);

    const chatEndRef = useRef(null);   // ref persists without triggering re-render

    // ========================================================================
    // SECTION 2 - SIDE EFFECTS
    // ========================================================================

    // Auto-scroll after every render where messages or loading changed.
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    // Health check on mount. Empty dependency array = run once.
    useEffect(() => {
        axios.get(`${API_BASE}/health`)
            .then(res => setHealth(res.data))
            .catch(() => setError(
                "Cannot reach the backend on port 5000. Start it with: python app.py"
            ));
    }, []);

    // ========================================================================
    // SECTION 3 - SEND MESSAGE
    // ========================================================================

    const handleSend = async (overrideText) => {
        const text = (overrideText ?? input).trim();
        if (text === "" || loading) return;

        setError(null);

        const newMessage = { role: 'user', content: text };
        const conversation = [...messages, newMessage];
        setMessages(conversation);
        setInput("");
        setLoading(true);

        try {

            const payload = {
                messages: conversation.map(m => ({ role: m.role, content: m.content })),
                temperature
            };

            const response = await axios.post(`${API_BASE}/chat`, payload);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.data.response,
                sources: response.data.sources || [],
                grounded: response.data.grounded
            }]);

        } catch (err) {

            const serverMsg = err.response?.data?.error;
            const msg = serverMsg || err.message || "Unknown error";
            console.error('Error getting bot response:', err);
            setError(msg);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I couldn't complete that request. Check that the backend " +
                         "is running and that the knowledge base has been loaded.",
                sources: [],
                grounded: false
            }]);
        } finally {
            setLoading(false);  
        }
    };

    const handleClear = () => {
        setMessages([{
            role: 'assistant',
            content: "Conversation cleared. What would you like to know?",
            sources: [],
            grounded: true
        }]);
        setError(null);
    };

    // ========================================================================
    // SECTION 4 - MESSAGE RENDERER
    // ========================================================================

    const renderMessage = (message, index) => {
        const isUser = message.role === "user";

        return (
            <Box
                key={index}
                display="flex"
                flexDirection="column"
                alignItems={isUser ? "flex-end" : "flex-start"}
                mb={1.5}
            >
                <Card
                    sx={{
                        bgcolor: isUser ? "#1976d2" : "#e8eaed",
                        color: isUser ? "#fff" : "#333",
                        borderRadius: 3,
                        maxWidth: "78%",
                        boxShadow: 2,
                        px: 2,
                        py: 1
                    }}
                >
                    <CardContent sx={{ p: 0, "&:last-child": { pb: 1 } }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {isUser ? "You" : "Assistant"}
                        </Typography>
                        <Divider sx={{ my: 0.5, opacity: 0.3 }} />
                        {/* pre-wrap preserves the model's line breaks and lists */}
                        <Typography
                            variant="body1"
                            sx={{ wordBreak: "break-word", whiteSpace: "pre-wrap", textAlign: "left" }}
                        >
                            {message.content}
                        </Typography>
                    </CardContent>
                </Card>

                {/* Citations - makes each answer verifiable and auditable */}
                {!isUser && message.sources?.length > 0 && (
                    <Box sx={{ maxWidth: "78%", mt: 0.75 }}>
                        <Typography variant="caption" color="textSecondary"
                            sx={{ display: 'block', mb: 0.5, letterSpacing: 0.4 }}>
                            SOURCES
                        </Typography>
                        <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap>
                            {message.sources.map((s, j) => (
                                <Tooltip
                                    key={j}
                                    title={`${s.doc_type} | owner: ${s.owner}` +
                                           (s.effective_date ? ` | effective ${s.effective_date}` : '')}
                                >
                                    <Chip
                                        size="small"
                                        icon={<DescriptionIcon />}
                                        label={`${s.source_document} (${Math.round(s.similarity * 100)}%)`}
                                        variant="outlined"
                                        sx={{ fontSize: 11 }}
                                    />
                                </Tooltip>
                            ))}
                        </Stack>
                    </Box>
                )}

                {/* Warn when no supporting document was retrieved */}
                {!isUser && message.grounded === false && (
                    <Alert
                        severity="warning"
                        icon={<WarningAmberIcon fontSize="inherit" />}
                        sx={{ mt: 0.75, maxWidth: "78%", py: 0, fontSize: 12 }}
                    >
                        No supporting document was found. This answer is not grounded
                        in the knowledge base - verify before acting on it.
                    </Alert>
                )}
            </Box>
        );
    };

    // ========================================================================
    // SECTION 5 - RENDER
    // ========================================================================

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: "100vh", bgcolor: "#f4f6fb" }}>

            {/* ---- HEADER ---- */}
            <AppBar position='static' elevation={2} sx={{ borderRadius: 0 }}>
                <Toolbar>
                    <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" component='div'>
                            Capacity Planning Knowledge Assistant
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                            Retrieval-Augmented Generation over approved documentation
                        </Typography>
                    </Box>

                    {/* Distinguishes "API down" from "knowledge base empty" */}
                    {health && (
                        <Chip
                            size="small"
                            label={`${health.knowledge_chunks} chunks indexed`}
                            color={health.knowledge_chunks > 0 ? "success" : "warning"}
                            sx={{ mr: 1 }}
                        />
                    )}

                    <Tooltip title="Clear conversation">
                        <IconButton color="inherit" onClick={handleClear}>
                            <DeleteSweepIcon />
                        </IconButton>
                    </Tooltip>
                </Toolbar>
            </AppBar>

            {/* ---- TEMPERATURE CONTROL ---- */}
            <Box sx={{
                display: 'flex', alignItems: 'center', gap: 2,
                px: 3, py: 1, bgcolor: "#fff", borderBottom: "1px solid #e0e0e0"
            }}>
                <Typography variant="caption" sx={{ fontWeight: 600, minWidth: 100 }}>
                    Response style
                </Typography>
                <Slider
                    size="small"
                    value={temperature}
                    min={0} max={1} step={0.1}
                    marks
                    valueLabelDisplay="auto"
                    onChange={(e, v) => setTemperature(v)}
                    sx={{ maxWidth: 200 }}
                />
                <Typography variant="caption" color="textSecondary" sx={{ fontStyle: 'italic' }}>
                    {tempHint(temperature)}
                </Typography>
            </Box>

            {/* ---- ERROR BANNER ---- */}
            <Collapse in={Boolean(error)}>
                <Alert severity="error" onClose={() => setError(null)} sx={{ borderRadius: 0 }}>
                    {error}
                </Alert>
            </Collapse>

            {/* ---- CHAT HISTORY ---- */}
            <Paper
                sx={{ flex: 1, p: 2, overflowY: 'auto', borderRadius: 0, bgcolor: "#f9fafb" }}
                elevation={0}
            >
                {messages.map(renderMessage)}

                {loading && (
                    <Box display="flex" alignItems="center" mb={1}>
                        <CircularProgress size={22} />
                        <Typography variant="body2" color="textSecondary" ml={2}>
                            Searching documentation...
                        </Typography>
                    </Box>
                )}

                <div ref={chatEndRef} />
            </Paper>

            {/* ---- STARTER PROMPTS ---- */}
            {messages.length <= 1 && (
                <Box sx={{ px: 2, py: 1.5, bgcolor: "#fff", borderTop: "1px solid #eee" }}>
                    <Typography variant="caption" color="textSecondary"
                        sx={{ display: 'block', mb: 1 }}>
                        Try one of these:
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                        {SUGGESTED_PROMPTS.map((p, i) => (
                            <Button
                                key={i}
                                size="small"
                                variant="outlined"
                                sx={{ textTransform: 'none', fontSize: 12, borderRadius: 5 }}
                                onClick={() => handleSend(p)}
                            >
                                {p}
                            </Button>
                        ))}
                    </Stack>
                </Box>
            )}

            {/* ---- INPUT ---- */}
            <Box sx={{
                display: 'flex', alignItems: 'center', p: 2,
                bgcolor: "#fff", borderTop: "1px solid #e0e0e0"
            }}>
                <TextField
                    variant='outlined'
                    fullWidth
                    multiline
                    maxRows={4}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder='Ask about capacity planning, productivity metrics, site attribution, cash allocation...'
                    onKeyDown={e => {
                     
                        if (e.key === "Enter" && !e.shiftKey && !loading) {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    sx={{ mr: 2, bgcolor: "#f4f6fb", borderRadius: 2 }}
                    disabled={loading}
                />
                <IconButton
                    color='primary'
                    onClick={() => handleSend()}
                    disabled={loading || input.trim() === ""}
                >
                    <SendIcon />
                </IconButton>
            </Box>

            <Typography variant="caption" color="textSecondary"
                sx={{ textAlign: 'center', pb: 1, px: 2 }}>
                Answers are generated from indexed documentation and may be incomplete.
                Verify figures against the system of record before making decisions.
            </Typography>
        </Box>
    );
};

export default Chatbot;
