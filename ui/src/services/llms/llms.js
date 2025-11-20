import { GoogleGenAI } from '@google/genai'
import { prompts } from './prompts'

export async function evaluateEssay(topic, content, model) {
    if (model === 'gemini') {
        evaluateEssayWithGemini(content)
    } else if (model === 'chatgpt') {
        evaluateEssayWithChatGpt(content)
    } else if (model === 'maritaca') {
        evaluateEssayWithMaritacaAi(content)
    }
}

async function evaluateEssayWithGemini(content) {
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

    for (const competency in prompts.zeroShot) {
        const prompt = prompts.zeroShot[competency]

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash-preview-09-2025',
            contents: content,
            config: {
                systemInstruction: prompt,
                ...generationConfig
            }
        })
        console.log(response)
    }
}

async function evaluateEssayWithChatGpt() {
    console.log('evaluating essay with chatgpt')
}

async function evaluateEssayWithMaritacaAi() {
    console.log('evaluating essay with sabia')
}
