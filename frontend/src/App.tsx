import { useState } from "react";
import { 
  Search, 
  Cpu, 
  TrendingDown, 
  AlertCircle, 
  ExternalLink, 
  LayoutGrid, 
  List, 
  Zap,
  BarChart3,
  Loader2
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn, formatCurrency } from "./lib/utils";

interface Product {
  titulo: string;
  preco: number;
  link: string;
  is_deal?: boolean;
}

interface SearchStats {
  total_found: number;
  valid_items: number;
  median_price: number;
  deal_threshold: number;
}

interface SearchResponse {
  search_term: string;
  stats: SearchStats;
  deals: Product[];
  others: Product[];
  error?: string;
}

export default function App() {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(`/search?item=${encodeURIComponent(query)}`);
      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || "Erro ao processar a busca.");
      }

      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha na conexão com a API.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/30 font-sans">
      {/* Header / Background Glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-64 bg-primary/5 blur-[120px] -z-10" />

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <header className="mb-12 text-center">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-mono mb-4"
          >
            <Cpu size={14} />
            <span>v1.0.0 STABLE</span>
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-4xl md:text-6xl font-bold tracking-tight mb-4"
          >
            Buscador de <span className="text-primary">Ofertas</span>
          </motion.h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Análise estatística em tempo real para encontrar as melhores ofertas de hardware no Mercado Livre.
          </p>
        </header>

        {/* Search Bar Area */}
        <div className="max-w-2xl mx-auto mb-16">
          <form onSubmit={handleSearch} className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/50 to-primary/30 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-500" />
            <div className="relative flex items-center bg-card border border-border rounded-2xl p-2 shadow-2xl">
              <div className="pl-4 text-muted-foreground">
                <Search size={20} />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ex: RTX 4060, RX 7600, Monitor 144Hz..."
                className="w-full bg-transparent border-none focus:ring-0 px-4 py-3 text-lg outline-none"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold flex items-center gap-2 hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 disabled:active:scale-100"
              >
                {isLoading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <>
                    <Zap size={18} fill="currentColor" />
                    <span>Buscar</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive flex items-center gap-3"
            >
              <AlertCircle size={20} />
              <p className="text-sm font-medium">{error}</p>
            </motion.div>
          )}
        </div>

        {/* Results Section */}
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div 
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-12"
            >
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-32 bg-card border border-border rounded-2xl animate-pulse" />
                ))}
              </div>
              <div className="space-y-6">
                <div className="h-8 w-48 bg-muted rounded animate-pulse" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-64 bg-card border border-border rounded-2xl animate-pulse" />
                  ))}
                </div>
              </div>
            </motion.div>
          ) : results && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-12"
            >
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard 
                  label="Itens Encontrados" 
                  value={results.stats.total_found} 
                  icon={<Search size={18} />} 
                />
                <StatCard 
                  label="Itens Válidos" 
                  value={results.stats.valid_items} 
                  sub="após filtro de ruído"
                  icon={<LayoutGrid size={18} />} 
                />
                <StatCard 
                  label="Mediana de Preço" 
                  value={formatCurrency(results.stats.median_price)} 
                  icon={<BarChart3 size={18} />} 
                  highlight
                />
                <StatCard 
                  label="Meta de Oferta" 
                  value={`< ${formatCurrency(results.stats.deal_threshold)}`} 
                  icon={<TrendingDown size={18} />} 
                  color="text-primary"
                />
              </div>

              {/* View Controls & Sections */}
              <div className="space-y-8">
                <div className="flex items-center justify-between border-b border-border pb-4">
                  <h2 className="text-2xl font-bold flex items-center gap-3">
                    <TrendingDown className="text-primary" />
                    Ofertas Imperdíveis
                    <span className="text-xs font-mono bg-primary/10 text-primary px-2 py-0.5 rounded uppercase tracking-wider">
                      {results.deals.length} Encontradas
                    </span>
                  </h2>
                  <div className="flex bg-muted rounded-lg p-1">
                    <button 
                      onClick={() => setViewMode("grid")}
                      className={cn("p-2 rounded-md transition-colors", viewMode === "grid" ? "bg-background shadow-sm text-primary" : "text-muted-foreground")}
                    >
                      <LayoutGrid size={18} />
                    </button>
                    <button 
                      onClick={() => setViewMode("list")}
                      className={cn("p-2 rounded-md transition-colors", viewMode === "list" ? "bg-background shadow-sm text-primary" : "text-muted-foreground")}
                    >
                      <List size={18} />
                    </button>
                  </div>
                </div>

                {results.deals.length > 0 ? (
                  <div className={cn(
                    "grid gap-6",
                    viewMode === "grid" ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" : "grid-cols-1"
                  )}>
                    {results.deals.map((product, i) => (
                      <ProductCard key={i} product={product} isDeal viewMode={viewMode} index={i} />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 bg-muted/30 rounded-3xl border border-dashed border-border">
                    <p className="text-muted-foreground">Nenhuma oferta abaixo do limite estatístico encontrada.</p>
                  </div>
                )}

                {results.others.length > 0 && (
                  <div className="pt-12 space-y-8">
                    <h2 className="text-xl font-semibold text-muted-foreground flex items-center gap-2">
                      Demais Resultados
                      <span className="text-xs font-mono bg-muted text-muted-foreground px-2 py-0.5 rounded">
                        {results.others.length} Itens
                      </span>
                    </h2>
                    <div className={cn(
                      "grid gap-4",
                      viewMode === "grid" ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-4" : "grid-cols-1"
                    )}>
                      {results.others.map((product, i) => (
                        <ProductCard key={i} product={product} viewMode={viewMode} index={i} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-24 py-12 bg-card/50">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Cpu size={18} />
            <span className="font-semibold text-foreground">Buscador de Ofertas</span>
            <span className="text-sm">© 2026 - Ferramenta de Estudo</span>
          </div>
          <div className="flex gap-8 text-sm text-muted-foreground">
            <a href="/docs" className="hover:text-primary transition-colors">API Docs</a>
            <a href="https://github.com" target="_blank" className="hover:text-primary transition-colors">Source Code</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function StatCard({ label, value, icon, sub, highlight, color }: { 
  label: string; 
  value: string | number; 
  icon: React.ReactNode; 
  sub?: string;
  highlight?: boolean;
  color?: string;
}) {
  return (
    <div className={cn(
      "p-6 rounded-2xl border transition-all hover:border-primary/50",
      highlight ? "bg-primary/5 border-primary/20" : "bg-card border-border"
    )}>
      <div className="flex items-center gap-3 text-muted-foreground mb-3">
        {icon}
        <span className="text-xs font-bold uppercase tracking-widest">{label}</span>
      </div>
      <div className={cn("text-2xl font-bold tracking-tight", color)}>
        {value}
      </div>
      {sub && <div className="text-[10px] text-muted-foreground mt-1 uppercase font-mono">{sub}</div>}
    </div>
  );
}

function ProductCard({ product, isDeal, viewMode, index }: { 
  product: Product; 
  isDeal?: boolean; 
  viewMode: "grid" | "list";
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4 }}
      className={cn(
        "group relative bg-card border border-border rounded-2xl overflow-hidden transition-all hover:shadow-2xl hover:border-primary/30",
        isDeal && "neon-glow ring-1 ring-primary/20",
        viewMode === "list" ? "flex items-center p-4 gap-6" : "p-6"
      )}
    >
      {isDeal && viewMode === "grid" && (
        <div className="absolute top-0 right-0 px-3 py-1 bg-primary text-primary-foreground text-[10px] font-bold uppercase tracking-tighter rounded-bl-xl">
          Melhor Preço
        </div>
      )}

      <div className={cn("flex-1", viewMode === "list" && "flex items-center justify-between gap-4")}>
        <h3 className={cn(
          "font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-2",
          viewMode === "grid" ? "text-lg mb-4 h-14" : "text-base max-w-2xl"
        )}>
          {product.titulo}
        </h3>
        
        <div className={cn(
          "flex items-baseline gap-2",
          viewMode === "grid" ? "flex-col" : "flex-row-reverse"
        )}>
          <span className={cn(
            "font-mono font-bold tracking-tighter",
            isDeal ? "text-3xl text-primary" : "text-xl text-foreground",
            viewMode === "list" && "min-w-[140px] text-right"
          )}>
            {formatCurrency(product.preco)}
          </span>
          {isDeal && (
            <span className="text-[10px] text-primary/70 font-bold uppercase tracking-widest">
              Abaixo da Mediana
            </span>
          )}
        </div>
      </div>

      <a 
        href={product.link} 
        target="_blank" 
        rel="noopener noreferrer"
        className={cn(
          "flex items-center justify-center gap-2 rounded-xl font-bold transition-all",
          isDeal 
            ? "bg-primary text-primary-foreground hover:brightness-110" 
            : "bg-secondary text-secondary-foreground hover:bg-secondary/80",
          viewMode === "grid" ? "w-full py-3 mt-6" : "px-6 py-2 ml-4 shrink-0"
        )}
      >
        <span>Ver Oferta</span>
        <ExternalLink size={16} />
      </a>
    </motion.div>
  );
}
