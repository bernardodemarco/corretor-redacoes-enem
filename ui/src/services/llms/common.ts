export function parseLlmResponse(response: any) {
    if (response == null || !['object', 'string'].includes(typeof response)) return null

    const parsedResponse = typeof response === 'string' ? JSON.parse(response) : response;
    console.log(response)
    return {
        score: parsedResponse.nota_atribuida,
        cot: parsedResponse.raciocinio_cot,
        feedback: parsedResponse.justificativa_para_aluno
    }
}
