import { GoogleGenAI } from '@google/genai'
import { prompts } from './prompts'
import { parseLlmResponse } from "./common"

const GEMINI_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY
const GEMINI_RESPONSE_SCHEMA = {
    type: 'object',
    properties: {
        nota_atribuida: { type: 'number' },
        raciocinio_cot: { type: 'string' },
        justificativa_para_aluno: { type: 'string' }
    },
    required: ['nota_atribuida', 'raciocinio_cot', 'justificativa_para_aluno']
}

export async function evaluateEssayWithGemini(content: string, model: string) {
    console.log(`Using ${model} to evaluate essay`)
    const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY })

    const llmRequests = prompts.zeroShot.map((prompt) => {
        return ai.models.generateContent({
            model: 'gemini-2.5-flash-preview-09-2025',
            contents: content,
            config: {
                systemInstruction: prompt,
                responseMimeType: 'application/json',
                responseSchema: GEMINI_RESPONSE_SCHEMA,
                temperature: 0.2
            }
        })
    })

    const responses = await Promise.all(llmRequests)
    return responses.map((response) => {
        const parsedResponse = parseLlmResponse(response?.text ?? response)
        if (parsedResponse) {
            return parsedResponse
        }
    })
}
