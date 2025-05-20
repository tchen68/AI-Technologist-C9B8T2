import React, { useState } from 'react';
import {Box, TextField, IconButton,
    Typography, Paper, List, ListItem, ListItemText,
    AppBar,
    Toolbar,
    CircularProgress
} from "@mui/material"
import SendIcon from "@mui/icons-material/Send"
import axios from 'axios'

const Chatbot = () => {
    const [messages, setMessages ]= useState([{role: 'system', content: 'You are a helpful assistant designed to answer questions in a clear, concise manner. You may be provided context in relation to the user prompt. Use it if it it is relevant to the user prompt.'}]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false)
    
    //Append the user's input to the conversation, get the bot's response, and append the response to the chat's history if it returns
    const handleSend = async () => {
        if (input.trim() === "") return;

        const newMessage = {role: 'user', content: input}
        const conversation = [...messages, newMessage]
        setMessages(conversation);
        setInput("")

        setLoading(true); // Set loading to true when sending a message
        const botResponse = await getBotResponse(conversation)
        setLoading(false); // Set loading to false after receiving the response

        setTimeout(() =>{
            const botMessage = {role: 'assistant', content: botResponse || 'Sorry, something went wrong. Please check the api service logs.'}
            setMessages(prevMessages => [...prevMessages, botMessage]);
        }, 1000)
    }

    //API call to get the bot's response
    const getBotResponse = async (conversationHistory) => {
        console.log("conversation history in get bot response: ", conversationHistory)
        setLoading(true)
        try {
            const response = await axios.post('http://localhost:5000/chat', {
                messages: conversationHistory,
            });
            
            const botResponse = response.data.response
            console.log("bot Response: ", response.data.response)

            setLoading(false)
            return botResponse
        } catch (error) {
            console.error('Error getting bot response:', error)
            setLoading(false)
            return null
        }
    };

return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: "space-between",
        height: "100vh",
        padding: 2
      }}
    >
        <AppBar position='static'>
            <Toolbar>
                <Typography variant="h6" component='div' sx={{flexGrow: 1}}>
                    AI Technologist Course Chatbot
                </Typography>
            </Toolbar>
        </AppBar>
        {/* CHAT HISTORY*/}
        <Paper
          sx={{
            flex: 1,
            padding: 2,
            marginBottom: 2,
            maxHeight: '70vh',
            overflowY: 'auto'
          }}
          elevation={3}
        >
            <List>
                {messages.map((message, index) => (
                    <ListItem key={index}>
                        <ListItemText
                            primary={
                                <Typography
                                  variant='body1'
                                  sx={{ color: message.role === "user" ? "blue" : message.role === "assistant" ? "green" : "orange"}}>
                                    {message.role === "user" ? "You: " : message.role === "system" ? "system: " : "Bot: "}
                                    {message.content}
                                </Typography>
                            }
                        />
                    </ListItem>
                ))}
                {loading && (
                    <ListItem>
                        <CircularProgress />
                    </ListItem>
                )}
            </List>
        </Paper>

        {/*INPUT FIELD AND SEND BUTTON*/}
        <Box sx={{display: 'flex'}}>
            <TextField
              variant='outlined'
              fullWidth
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder='Type your message here...'
            />
            <IconButton color='primary' onClick={handleSend}>
                <SendIcon/>
            </IconButton>
        </Box>
    </Box>
)};

export default Chatbot;