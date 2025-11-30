import { evaluateEssayWithGemini } from './gemini';
import { evaluateEssayWithMaritacaAi } from './maritaca';

export async function evaluateEssay(topic: string, content: string, model: string) {
    let evaluator;
    if (model === 'gemini') {
        evaluator = evaluateEssayWithGemini
    } else {
        evaluator = evaluateEssayWithMaritacaAi
    }

    return await evaluator(content, model)
}
