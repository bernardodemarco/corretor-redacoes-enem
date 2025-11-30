import { prompts } from './prompts'
import axios from 'axios'
import { parseLlmResponse } from './common'

export async function evaluateEssayWithMaritacaAi(content: string, model: string) {
    console.log(`Using ${model} to evaluate essay`)
    try {
        const responses = await Promise.all(getMaritacaAiRequests(content))
        return responses.map((response) => {
            const parsedResponse = parseLlmResponse(response.data)
            if (parsedResponse) {
                return parsedResponse
            }
        })
    } catch (error) {
        console.error("Error sending chat request:", error);
        throw error;
    }
}

function getMaritacaAiRequests(content: string) {
    return prompts.zeroShot.map((prompt) => {
        return axios.post('http://localhost:3000/essay', {
            essayContent: content,
            prompt
        })
    })
}
