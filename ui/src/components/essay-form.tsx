import { useState } from 'react';
import { Button } from './button';
import { Input } from './input';
import { Textarea } from './textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select';
import { Label } from './label';
import { Card } from './card';
import { Upload } from 'lucide-react';
import { LoadingOverlay } from './loading-overlay';

export function EssayForm() {
  const [essayTopic, setEssayTopic] = useState('');
  const [essayContent, setEssayContent] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true)
    console.log('Essay evaluation submitted:', {
      topic: essayTopic,
      content: essayContent,
      model: selectedModel
    })
    try {
      await new Promise(resolve => setTimeout(resolve, 3000))
      console.log('Essay was successfully evaluated!!!')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>

      {isLoading && <LoadingOverlay />}

      <Card className="w-full max-w-2xl mx-auto p-8 bg-card/50 border-border backdrop-blur-sm">
        <div className="flex items-center justify-center gap-3">
          <div className="md:w-12 md:h-12 h-10 w-10 bg-primary/20 rounded-lg flex items-center justify-center">
            <Upload className="md:w-6 md:h-6 w-4 h-4 text-primary" />
          </div>
          <h2 className="text-foreground sm:text-3xl text-2xl font-bold tracking-tight md:text-2xl">Envie a sua redação</h2>
        </div>
        
        <p className="text-muted-foreground text-lg sm:text-xl mb-3 w-full text-center ">
          Insira o tema da redação e o seu conteúdo nos campos abaixo.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="topic" className="text-foreground text-lg sm:text-xl font-bold tracking-tight">Tema da Redação</Label>
            <Input
              id="topic"
              placeholder="Insira o tema da redação..."
              value={essayTopic}
              onChange={(e) => setEssayTopic(e.target.value)}
              className="bg-input-background border-border text-foreground placeholder:text-muted-foreground focus:bg-input-background autofill:bg-input-background"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="content" className="text-foreground text-lg sm:text-xl font-bold tracking-tight">Conteúdo da Redação</Label>
            <Textarea
              id="content"
              placeholder="Insira o conteúdo da sua redação em formato de texto..."
              value={essayContent}
              onChange={(e) => setEssayContent(e.target.value)}
              className="min-h-32 bg-input-background border-border text-foreground placeholder:text-muted-foreground resize-y"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-foreground text-lg sm:text-xl font-bold tracking-tight">Modelo de Avaliação</Label>
            <Select onValueChange={setSelectedModel}>
              <SelectTrigger className="bg-input-background border-border text-foreground cursor-pointer">
                <SelectValue placeholder="Selecione um modelo de IA para avaliação da redação" />
              </SelectTrigger>
              <SelectContent className="bg-card border-border">
                <SelectItem value="gemini">Gemini Pro (Google)</SelectItem>
                <SelectItem value="deep-seek">DeepSeek</SelectItem>
                <SelectItem value="maritaca">Maritaca AI</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground cursor-pointer"
            disabled={!essayTopic || !essayContent || !selectedModel}
          >
            <Upload className="w-4 h-4 mr-2" />
            Avaliar redação
          </Button>
        </form>
      </Card>
    </>
  )
}
