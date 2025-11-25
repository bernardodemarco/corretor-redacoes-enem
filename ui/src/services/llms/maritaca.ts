import { prompts } from './prompts'
import axios from 'axios'

const MARITACA_API_KEY = import.meta.env.VITE_MARITACA_API_KEY
const CHAT_API_URL = "https://chat.maritaca.ai/api/chat/inference";
const MARITACA_RESPONSE_SCHEMA = {
    type: 'object',
    schema: {
        properties: {
            nota_atribuida: { type: 'number' },
            raciocinio_cot: { type: 'string' },
            justificativa_para_aluno: { type: 'string' }
        },
        required: ['nota_atribuida', 'raciocinio_cot', 'justificativa_para_aluno']
    }
}

export async function evaluateEssayWithMaritacaAi(content: string, model: string) {
    console.log(`Using ${model} to evaluate essay`)
    try {
        const responses = await Promise.all(getMaritacaAiRequests(content))
        console.log(responses)
    } catch (error) {
        console.error("Error sending chat request:", error);
        throw error;
    }
}

function getMaritacaAiRequests(content: string) {
    return prompts.zeroShot.map((prompt) => {
        const payload = {
            messages: [
                { "role": "user", content },
                { "role": "system", content: prompt }
            ],
            // do_sample: true,
            // max_tokens: 50,
            temperature: 0.2,
            top_p: 0.95,
            model: "sabia-3",
            response_format: {
                'type': 'json_schema',
                'json_schema': MARITACA_RESPONSE_SCHEMA
            }
        }

        return axios.post(CHAT_API_URL, payload, {
            headers: {
                'Authorization': `Key ${MARITACA_API_KEY}`,
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        })
    })
}
