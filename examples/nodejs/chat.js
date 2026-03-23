/** FreeLLMShare — Basic Chat. Usage: npm install openai && node chat.js */
import OpenAI from 'openai';
const client = new OpenAI({ baseURL: 'https://aiapiv2.pekpik.com/v1', apiKey: 'YOUR_KEY_HERE' });
const r = await client.chat.completions.create({ model: 'gpt-5.4', messages: [{ role: 'user', content: 'Hello!' }] });
console.log(r.choices[0].message.content);
