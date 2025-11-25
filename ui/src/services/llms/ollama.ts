import { prompts } from './prompts'
import axios from 'axios'

const CHAT_API_URL = "http://localhost:11434/api/chat";
const OLLAMA_RESPONSE_SCHEMA = {
    type: 'object',
    properties: {
        nota_atribuida: { type: 'number' },
        raciocinio_cot: { type: 'string' },
        justificativa_para_aluno: { type: 'string' }
    },
    required: ['nota_atribuida', 'raciocinio_cot', 'justificativa_para_aluno']
}

export async function evaluateEssayWithOllama(content: string, model: string) {
    console.log(`Using ${model} to evaluate essay`)
    try {
        const responses = await Promise.all(getOllamaRequests(content, model))
        console.log(responses)
    } catch (error) {
        console.error("Error sending chat request:", error);
        throw error;
    }
}

function getOllamaRequests(content: string, model: string) {
    return prompts.zeroShot.map((prompt) => {
        const payload = {
            messages: [
                { "role": "user", content },
                { "role": "system", content: prompt }
            ],
            model,
            stream: false,
            response_format: {
                'type': 'json_schema',
                'json_schema': OLLAMA_RESPONSE_SCHEMA
            }
        }

        return axios.post(CHAT_API_URL, payload, {
            headers: {
                'Content-Type': 'application/json',
            }
        })
    })
}
