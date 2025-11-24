import { GoogleGenAI } from '@google/genai'
import { prompts } from './prompts'

export async function evaluateEssay(topic: string, content: string, model: string) {
    let evaluator;
    if (model === 'gemini') {
        evaluator = evaluateEssayWithGemini
    } else if (model === 'chatgpt') {
        evaluator = evaluateEssayWithChatGpt
    } else {
        evaluator = evaluateEssayWithMaritacaAi
    }

    return await evaluator(content)
}

async function evaluateEssayWithGemini(content: string) {
    const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY
    const ai = new GoogleGenAI({ apiKey: GOOGLE_API_KEY })

    const jsonSchema = {
        type: 'object',
        properties: {
            nota_atribuida: { type: 'number' },
            raciocinio_cot: { type: 'string' },
            justificativa_para_aluno: { type: 'string' }
        },
        required: ['nota_atribuida', 'raciocinio_cot', 'justificativa_para_aluno']
    }

    const generationConfig = {
        responseMimeType: 'application/json',
        responseSchema: jsonSchema,
        temperature: 0.2
    }

    const llmRequests = prompts.zeroShot.map((prompt) => {
        return ai.models.generateContent({
            model: 'gemini-2.5-flash-preview-09-2025',
            contents: content,
            config: {
                systemInstruction: prompt,
                ...generationConfig
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

async function evaluateEssayWithChatGpt(content: string) {
    console.log('evaluating essay with chatgpt')
}

async function evaluateEssayWithMaritacaAi(content: string) {
    console.log('evaluating essay with sabia')
}

function parseLlmResponse(response: any) {
    if (response == null || !['object', 'string'].includes(typeof response)) return null

    const parsedResponse = typeof response === 'string' ? JSON.parse(response) : response;
    return {
        score: parsedResponse.nota_atribuida,
        cot: parsedResponse.raciocinio_cot,
        feedback: parsedResponse.justificativa_para_aluno
    }
}
