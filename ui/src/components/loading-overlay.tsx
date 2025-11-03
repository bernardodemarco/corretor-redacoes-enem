import { Loader2 } from 'lucide-react';
import { motion } from 'motion/react';

interface LoadingOverlayProps {
  message?: string;
}

export function LoadingOverlay({ message = "Avaliando redação..." }: LoadingOverlayProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col items-center gap-4 p-8 rounded-lg bg-card border border-border shadow-2xl"
      >
        <div className="relative">
          {/* Outer spinning ring */}
          <div className="absolute inset-0 rounded-full border-4 border-primary/20" />
          
          {/* Animated spinner */}
          <Loader2 className="w-16 h-16 text-primary animate-spin" />
          
          {/* Pulsing glow effect */}
          <div className="absolute inset-0 rounded-full bg-primary/20 blur-xl animate-pulse" />
        </div>
        
        <div className="text-center space-y-2">
          <h3 className="text-foreground">{message}</h3>
          <p className="text-muted-foreground">Isso pode levar uns minutos</p>
        </div>
        
        {/* Progress dots */}
        <div className="flex gap-2">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-2 h-2 rounded-full bg-primary"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2,
              }}
            />
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
