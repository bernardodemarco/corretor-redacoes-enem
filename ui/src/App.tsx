import { EssayForm } from "./components/essay-form";

export function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-emerald-900/30">
      <div className="container mx-auto px-4 pt-12 pb-10">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary mb-8">
            <span className="w-2 h-2 bg-primary rounded-full"></span>
            INE5687 - Projeto em Ciência de Dados
          </div>
          
          <h1 className="mb-6">
            <span className="block text-foreground text-5xl md:text-6xl font-black tracking-tight">Corretor de Redações</span>
            <span className="block text-primary text-5xl md:text-6xl font-black tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">ENEM</span>
          </h1>
          
          <p className="text-muted-foreground max-w-4xl mx-auto text-xl">
            Obtenha feedback de suas redações do ENEM. Preencha o tema da redação, insira o seu conteúdo e selecione o modelo para avaliação.
          </p>
        </div>

        <EssayForm />
      </div>

      <footer className='flex justify-center border-t border-primary/20 w-98/100 mx-auto'>
        <p className="text-muted-foreground my-4 text-base text-center">
            Por <a href="https://github.com/bernardodemarco" className="hover:text-foreground hover:font-semibold transition-colors hover:underline-offset-1">Bernardo De Marco Gonçalves</a>, <a href="https://github.com/lucaslazarinii" className="hover:text-foreground hover:font-semibold transition-colors hover:underline-offset-1">Lucas Almeida Lazarini</a>, <a href="https://github.com/devpedrorocha" className="hover:text-foreground hover:font-semibold transition-colors hover:underline-offset-1">Pedro Henrique Nascimento Rocha</a> e <a href="https://github.com/VitorValandro" className="hover:text-foreground hover:font-semibold transition-colors hover:underline-offset-1">Vitor Matheus Valandro da Rosa</a>
        </p>
      </footer>
    </div>
  )
}
