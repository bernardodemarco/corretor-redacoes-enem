import { useState } from 'react';
import { Button } from './button';
import { Input } from './input';
import { Textarea } from './textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select';
import { Label } from './label';
import { Card } from './card';
import { Upload } from 'lucide-react';

export function EssayForm() {
  const [essayTopic, setEssayTopic] = useState('');
  const [essayContent, setEssayContent] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Essay evaluation submitted:', {
      topic: essayTopic,
      content: essayContent,
      model: selectedModel
    });
    // Here you would typically send the data to your evaluation service
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      // Handle file upload here
      console.log('File dropped:', e.dataTransfer.files[0]);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto p-8 bg-card/50 border-border backdrop-blur-sm">
      <div className="flex items-center justify-center gap-3">
        <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
          <Upload className="w-6 h-6 text-primary" />
        </div>
        <h2 className="text-foreground text-3xl font-bold tracking-tight">Envie a sua redação</h2>
      </div>
      
      <p className="text-muted-foreground text-xl mb-3 w-full text-center">
        Insira o tema da redação e o seu conteúdo nos campos abaixo.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="topic" className="text-foreground text-xl font-bold tracking-tight">Tema da Redação</Label>
          <Input
            id="topic"
            placeholder="Insira o tema da redação..."
            value={essayTopic}
            onChange={(e) => setEssayTopic(e.target.value)}
            className="bg-input-background border-border text-foreground placeholder:text-muted-foreground"
          />
        </div>

        <div className="space-y-2">
          <Label className="text-foreground text-xl font-bold tracking-tight">Imagem da Redação</Label>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive 
                ? 'border-primary bg-primary/5' 
                : 'border-border hover:border-primary/50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-foreground mb-1">Arraste e solte o seu arquivo aqui</p>
            <p className="text-muted-foreground mb-4">ou clique para navegar</p>
            <p className="text-sm text-muted-foreground">
              Formatos suportados: JPG, PNG, PDF
            </p>
            <p className="text-sm text-muted-foreground">
              Tamanho máximo do arquivo: 10MB
            </p>
            <input
              type="file"
              className="hidden"
              accept=".jpg,.jpeg,.png,.pdf"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  console.log('File selected:', e.target.files[0]);
                }
              }}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="content" className="text-foreground text-xl font-bold tracking-tight">Conteúdo da Redação</Label>
          <Textarea
            id="content"
            placeholder="Ou, insira o conteúdo da sua redação em formato de texto..."
            value={essayContent}
            onChange={(e) => setEssayContent(e.target.value)}
            className="min-h-32 bg-input-background border-border text-foreground placeholder:text-muted-foreground resize-y"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="model" className="text-foreground text-xl font-bold tracking-tight">Modelo de Avaliação</Label>
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
          disabled={!essayTopic || (!essayContent && !selectedModel)}
        >
          <Upload className="w-4 h-4 mr-2" />
          Avaliar redação
        </Button>
      </form>
    </Card>
  );
}
