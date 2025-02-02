import { workerData, parentPort } from 'worker_threads';
import { spawn } from 'child_process';

// Function to execute the Python script
async function runPythonProcess(word) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', ['python/processor.py']); // Ensure correct path

    pythonProcess.stdin.write(JSON.stringify({ word }) + '\n');
    pythonProcess.stdin.end();

    let output = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python error: ${data.toString()}`);
      reject(new Error('Python process error'));
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}`));
      } else {
        try {
          resolve(JSON.parse(output));
        } catch (err) {
          reject(new Error('Invalid JSON response from Python process'));
        }
      }
    });
  });
}

// Listen for messages from the main thread
(async () => {
  try {
    const result = await runPythonProcess(workerData.word);
    parentPort.postMessage(result);
  } catch (error) {
    parentPort.postMessage({ error: error.message });
  }
})();

