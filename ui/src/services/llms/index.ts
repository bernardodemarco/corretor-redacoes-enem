import { evaluateEssayWithGemini } from './gemini';
import { evaluateEssayWithMaritacaAi } from './maritaca';
import { evaluateEssayWithOllama } from './ollama';

export async function evaluateEssay(topic: string, content: string, model: string) {
    let evaluator;
    if (model === 'gemini') {
        evaluator = evaluateEssayWithGemini
    } else if (model === 'maritaca') {
        evaluator = evaluateEssayWithMaritacaAi
    } else {
        evaluator = evaluateEssayWithOllama
    }

    return await evaluator(content, model)
}
