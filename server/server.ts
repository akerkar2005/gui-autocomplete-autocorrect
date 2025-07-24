/*
 * In a production setting, the following code would
 * be the worker we use to handle requests. This is
 * an Express server backend with rate-limiting and CORS
 * options.
 */

import express, { Request, Response } from 'express';
import rateLimit from 'express-rate-limit';
import cors from 'cors';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import Piscina from 'piscina';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const workerPool = new Piscina({
  filename: path.resolve(__dirname, 'pythonWorker.js'),
  minThreads: 2,
  maxThreads: 4,
});



// Express app setup
const app = express();
const port = process.env.PORT || 3000;

const allowedOrigins = ['http://localhost:5173', 'http://100.80.0.51:5173'];

const corsOptions = {
  origin: (origin: string | undefined, callback: Function) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
  allowedHeaders: 'Content-Type,Authorization',
  credentials: true,
};


// Middleware
app.use(express.json());
app.use(cors(corsOptions));

// Initialize rate limiter
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests, please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Python process management
let pythonProcess: ChildProcess | null = null;

// Initialize Python backend
function initializePythonBackend(): Promise<void> {
  return new Promise((resolve, reject) => {
    console.log('Initializing Python backend...');
    pythonProcess = spawn('python', ['processor.py'], {
      cwd: path.join(__dirname, 'python') // This works with ES Modules
    });

    pythonProcess.stderr?.on('data', (data: Buffer) => {
      console.error(`Python error: ${data.toString()}`);
    });

    pythonProcess.on('close', (code: number) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}`));
      }
    });

    setTimeout(() => resolve(), 13000);
  });
}

// A queue to handle requests
let requestQueue: { word: string, resolve: Function, reject: Function }[] = [];
let isProcessing = false;

// Handle Python backend responses
pythonProcess?.stdout?.on('data', (data: Buffer) => {
  try {
    const result = JSON.parse(data.toString());
    const currentRequest = requestQueue.shift(); // Remove the first request from the queue
    if (currentRequest) {
      currentRequest.resolve(result);
    }
    isProcessing = false;
    processNextInQueue();
  } catch (error) {
    console.error('Error parsing Python response:', error);
    const currentRequest = requestQueue.shift();
    if (currentRequest) {
      currentRequest.reject(error);
    }
    isProcessing = false;
    processNextInQueue();
  }
});

// Consolidated word processing function
async function handleWordProcessing(word: string): Promise<string[]> {
  return new Promise((resolve, reject) => {
    if (!pythonProcess) {
      reject(new Error('Python backend not initialized'));
      return;
    }

    requestQueue.push({ word, resolve, reject });
    processNextInQueue();
  });
}

// Function to process the next word in the queue
function processNextInQueue() {
  if (isProcessing || requestQueue.length === 0) {
    return;
  }

  const currentRequest = requestQueue[0];
  isProcessing = true;

  const input = JSON.stringify({ word: currentRequest.word }) + '\n';
  if (!pythonProcess?.stdin?.write(input)) {
    pythonProcess.stdin.once('drain', () => {
      processNextInQueue();
    });
    return;
  }

  const onData = (data: Buffer) => {
    try {
      const result = JSON.parse(data.toString());
      currentRequest.resolve(result);
    } catch (err) {
      currentRequest.reject(err);
    } finally {
      isProcessing = false;
      requestQueue.shift();
      processNextInQueue();

      pythonProcess.stdout?.off('data', onData);
    }
  };

  pythonProcess.stdout?.on('data', onData);
}

// Routes
app.post('/api/autocorrect', async (
  req: Request<{}, {}, { input_word: string }>,
  res: Response<{ suggestions: string[], error?: string }>
) => {
  try {
    const { input_word } = req.body;
    if (!input_word) {
      return res.status(400).json({
        suggestions: [],
        error: 'Input word is required'
      });
    }

    const result = await handleWordProcessing(input_word);
    res.json({ suggestions: result });
  } catch (error) {
    console.error('Error processing word:', error);
    res.status(500).json({
      suggestions: [],
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

// Initialize server
async function startServer(): Promise<void> {
  try {
    await initializePythonBackend();
    app.listen(port, '0.0.0.0', () => {
      console.log(`Server running at http://localhost:${port}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  process.exit(0);
});

// Start the server
startServer().catch(error => {
  console.error('Failed to start server:', error);
  process.exit(1);
});

export default app;
