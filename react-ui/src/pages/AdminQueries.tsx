import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Mail, Calendar, MessageSquare } from "lucide-react";

interface UnresolvedQuery {
  id: string;
  originalMessage: string;
  query: string;
  userEmail: string;
  timestamp: Date;
}

const AdminQueries = () => {
  const navigate = useNavigate();
  const [queries, setQueries] = useState<UnresolvedQuery[]>([]);

  useEffect(() => {
    // Load unresolved queries from localStorage
    const savedQueries = localStorage.getItem('unresolvedQueries');
    if (savedQueries) {
      const parsed = JSON.parse(savedQueries);
      setQueries(parsed.map((query: any) => ({
        ...query,
        timestamp: new Date(query.timestamp)
      })));
    }
  }, []);

  const clearQueries = () => {
    localStorage.removeItem('unresolvedQueries');
    setQueries([]);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card px-4 py-3 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="font-semibold">Unresolved Queries</h1>
          <p className="text-sm text-muted-foreground">Customer feedback and queries</p>
        </div>
        <Badge variant="outline" className="ml-auto">
          {queries.length} queries
        </Badge>
      </div>

      <div className="p-4">
        {queries.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Unresolved Queries</h3>
              <p className="text-muted-foreground text-center">
                Customer queries that need attention will appear here
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold">Submitted Queries</h2>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearQueries}
                className="text-destructive hover:text-destructive"
              >
                Clear All
              </Button>
            </div>

            <div className="space-y-4">
              {queries.map((query) => (
                <Card key={query.id} className="border-l-4 border-l-warning">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-base">Query #{query.id.slice(-8)}</CardTitle>
                      <Badge variant="outline" className="text-xs">
                        New
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Mail className="h-3 w-3" />
                        <span>{query.userEmail}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{query.timestamp.toLocaleDateString()}</span>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {query.originalMessage && (
                      <div>
                        <h4 className="font-medium text-sm mb-2">Original Bot Response Context:</h4>
                        <div className="bg-muted p-3 rounded-lg text-sm">
                          {query.originalMessage}
                        </div>
                      </div>
                    )}
                    <div>
                      <h4 className="font-medium text-sm mb-2">Customer Query:</h4>
                      <div className="bg-card border rounded-lg p-3">
                        <p className="text-sm leading-relaxed">{query.query}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminQueries;