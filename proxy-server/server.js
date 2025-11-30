import express from 'express'
import cors from 'cors'
import OpenAI from 'openai'
const app = express()
const port = 3000

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
const client = new OpenAI({
    apiKey: process.env.MARITACA_API_KEY,
    baseURL: 'https://chat.maritaca.ai/api'
})

app.use(cors())
app.use(express.json())

app.post('/essay', async (req, res) => {
    try {
        const { essayContent, prompt } = req.body
        console.log('sending request to Maritaca...')
        const response = await client.chat.completions.create({
            model: 'sabia-3.1',
            messages: [
                { role: "system", content: prompt },
                { role: "user", content: essayContent }
            ],
            response_format: {
                type: "json_schema",
                json_schema: MARITACA_RESPONSE_SCHEMA
            },
            temperature: 0.2
        });
        console.log('returned from await')
        const jsonString = response.choices[0].message.content;
        const jsonData = JSON.parse(jsonString);
        res.json(jsonData)
    } catch (error) {
        console.log(error)
    }
})

app.listen(port, () => {
    console.log(`Server listening on port ${port}`)
})
