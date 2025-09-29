import { EssayForm } from "./components/essay-form";

export function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-emerald-900/30">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary mb-8">
            <span className="w-2 h-2 bg-primary rounded-full"></span>
            INE5687 - Projeto em Ciência de Dados
          </div>
          
          <h1 className="mb-6">
            <span className="block text-foreground text-6xl font-black tracking-tight">Corretor de Redações</span>
            <span className="block text-primary text-6xl font-black tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">ENEM</span>
          </h1>
          
          <p className="text-muted-foreground max-w-4xl mx-auto text-xl">
            Obtenha feedback de suas redações do ENEM. Preencha o tema da redação, anexe uma imagem da redação ou insira o seu conteúdo e selecione o modelo para avaliação.
          </p>
        </div>

        <EssayForm />
      </div>
    </div>
  )
}
