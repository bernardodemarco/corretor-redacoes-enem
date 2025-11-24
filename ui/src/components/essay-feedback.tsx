import { Button } from './button';
import { Label } from './label';
import { Card } from './card';
import { CornerDownLeft, GraduationCap } from 'lucide-react';


export type Competency = {
  id?: string;
  name: string;
  score: number;
  feedback: string;
  cot?: string; // chain-of-thought / model reasoning (optional)
}

type EssayFeedbackProps = {
  topic?: string;
  competencies: Competency[];
  onBack?: () => void;
}

export function EssayFeedback({ topic, competencies, onBack }: EssayFeedbackProps) {
  console.log('competencies:', competencies)
  const totalScore = competencies.reduce((acc, c) => acc + (c.score || 0), 0)
  return (
    <Card className="w-full max-w-3xl mx-auto p-8 bg-card/50 border-border backdrop-blur-sm gap-3">
      <div className="flex items-center justify-center gap-3">
          <div className="md:w-12 md:h-12 h-10 w-10 bg-primary/20 rounded-lg flex items-center justify-center">
            <GraduationCap className="md:w-6 md:h-6 w-4 h-4 text-primary" />
          </div>
          <h2 className="text-foreground sm:text-3xl text-2xl font-bold tracking-tight md:text-2xl">Avaliação da Redação</h2>
      </div>

      {topic && (
        <div className="mb-4 w-full text-center">
          <p className="text-muted-foreground font-semibold text-lg sm:text-xl">Tema: <span className="text-muted-foreground font-normal">{topic}</span></p>
          <div className="mt-3 inline-flex items-center justify-center bg-primary/10 rounded-md px-4 py-2">
            <span className="text-foreground font-bold text-2xl mr-2">{totalScore}</span>
            <span className="text-muted-foreground">/ {1000}</span>
          </div>
        </div>
      )}
      

      <div className="space-y-6">
        {competencies.map((c, idx) => {
          const pct = Math.max(0, Math.min(1, c.score / 200));
          const barWidth = `${Math.round(pct * 100)}%`;
          return (
            <div key={c.id ?? idx} className="bg-card/30 border border-border rounded-lg p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <Label className="text-foreground text-lg sm:text-xl font-bold tracking-tight">{c.name}</Label>
                  <div className="mt-2 w-full h-2 bg-border rounded overflow-hidden">
                    <div className="h-2 bg-primary" style={{ width: barWidth }} />
                  </div>
                </div>

                <div className="flex-shrink-0 text-right">
                  <div className="inline-flex items-center justify-center bg-primary/10 rounded-md px-3 py-2">
                    <span className="text-foreground font-bold text-xl">{c.score}</span>
                    <span className="text-muted-foreground ml-2">/200</span>
                  </div>
                </div>
              </div>

              <div className="mt-3">
                <p className="mt-1">
                  <span className="text-foreground font-medium">Comentário:&nbsp;</span>
                  <span className="text-muted-foreground whitespace-pre-line">{c.feedback}</span>
                </p>

                {c.cot && (
                  <details className="mt-3 bg-card/10 border border-border rounded-md p-3">
                    <summary className="cursor-pointer text-muted-foreground font-medium">Raciocínio do modelo</summary>
                    <pre className="mt-2 text-foreground whitespace-pre-wrap text-sm">{c.cot}</pre>
                  </details>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-4">
        {onBack && (
            <Button 
              type="button" 
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground cursor-pointer"
              onClick={onBack}
            >
              <CornerDownLeft className="w-4 h-4 mr-2" />
              Retornar
            </Button>          
          )}
        </div>
    </Card>
  )
}
