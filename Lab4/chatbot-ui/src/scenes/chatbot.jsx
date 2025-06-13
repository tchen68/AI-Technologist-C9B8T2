import React, { useState, useRef, useEffect } from 'react';
import {
    Box, TextField, IconButton, Typography, Paper, AppBar, Toolbar,
    CircularProgress, Card, CardContent, Divider
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import axios from 'axios';

const Chatbot = () => {
    const [messages, setMessages] = useState([
        { role: 'system', content: 'You are a helpful assistant designed to answer questions in a clear, concise manner. You may be provided context in relation to the user prompt. Use it if it it is relevant to the user prompt.' }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    const handleSend = async () => {
        if (input.trim() === "") return;
        const newMessage = { role: 'user', content: input };
        const conversation = [...messages, newMessage];
        setMessages(conversation);
        setInput("");
        setLoading(true);
        const botResponse = await getBotResponse(conversation);
        setLoading(false);
        setTimeout(() => {
            const botMessage = { role: 'assistant', content: botResponse || 'Sorry, something went wrong. Please check the api service logs.' };
            setMessages(prevMessages => [...prevMessages, botMessage]);
        }, 500);
    };

    const getBotResponse = async (conversationHistory) => {
        try {
            const response = await axios.post('http://localhost:5000/chat', {
                messages: conversationHistory,
            });
            return response.data.response;
        } catch (error) {
            console.error('Error getting bot response:', error);
            return null;
        }
    };

    const renderMessage = (message, index) => {
        if (message.role === "system") {
            return (
                <Box key={index} display="flex" justifyContent="center" my={2}>
                    <Typography variant="caption" color="textSecondary" sx={{ fontStyle: 'italic' }}>
                        System Role: {message.content}
                    </Typography>
                </Box>
            );
        }
        const isUser = message.role === "user";
        return (
            <Box
                key={index}
                display="flex"
                justifyContent={isUser ? "flex-end" : "flex-start"}
                alignItems="flex-end"
                mb={1}
            >
                <Card
                    sx={{
                        bgcolor: isUser ? "#1976d2" : "#e0e0e0",
                        color: isUser ? "#fff" : "#333",
                        borderRadius: 3,
                        maxWidth: "70%",
                        boxShadow: 2,
                        px: 2,
                        py: 1,
                        ml: isUser ? "auto" : 0,
                        mr: isUser ? 0 : "auto"
                    }}
                >
                    <CardContent sx={{ p: 0, "&:last-child": { pb: 1 } }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {isUser ? "You" : "Bot"}
                        </Typography>
                        <Divider sx={{ my: 0.5, opacity: 0.3 }} />
                        <Typography variant="body1" sx={{ wordBreak: "break-word" }}>
                            {message.content}
                        </Typography>
                    </CardContent>
                </Card>
            </Box>
        );
    };

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                height: "100vh",
                bgcolor: "#f4f6fb"
            }}
        >
            <AppBar position='static' elevation={2} sx={{ borderRadius: 0, mb: 1 }}>
                <Toolbar>
                    <Typography variant="h6" component='div' sx={{ flexGrow: 1 }}>
                        AI Technologist Course Chatbot
                    </Typography>
                </Toolbar>
            </AppBar>
            {/* CHAT HISTORY */}
            <Paper
                sx={{
                    flex: 1,
                    p: 2,
                    mb: 0,
                    maxHeight: '70vh',
                    overflowY: 'auto',
                    borderRadius: 3,
                    boxShadow: 3,
                    bgcolor: "#f9fafb"
                }}
                elevation={0}
            >
                {messages.map(renderMessage)}
                {loading && (
                    <Box display="flex" justifyContent="flex-start" alignItems="center" mb={1}>
                        <CircularProgress size={24} />
                        <Typography variant="body2" color="textSecondary" ml={2}>
                            Bot is typing...
                        </Typography>
                    </Box>
                )}
                <div ref={chatEndRef} />
            </Paper>
            {/* INPUT FIELD AND BUTTON */}
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    p: 2,
                    bgcolor: "#fff",
                    borderTop: "1px solid #e0e0e0",
                    boxShadow: "0 -2px 8px rgba(0,0,0,0.03)"
                }}
            >
                <TextField
                    variant='outlined'
                    fullWidth
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder='Type your message here...'
                    onKeyDown={e => {
                        if (e.key === "Enter" && !loading) handleSend();
                    }}
                    sx={{ mr: 2, bgcolor: "#f4f6fb", borderRadius: 2 }}
                    disabled={loading}
                />
                <IconButton color='primary' onClick={handleSend} disabled={loading || input.trim() === ""}>
                    <SendIcon />
                </IconButton>
            </Box>
        </Box>
    );
};

export default Chatbot;