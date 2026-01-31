import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Edit2, Plus, Trash2, Save, X, Tags } from "lucide-react";
import { useNavigate } from "react-router-dom";

// Default knowledge base structure
const DEFAULT_KNOWLEDGE = {
  service: {
    keywords: ["service", "maintenance", "schedule", "km", "ola", "ather", "tvs", "bajaj", "check"],
    responses: [
      "📅 **OLA S1/S1 Pro Service Schedule:**\n• First service: 500 km\n• Regular service: Every 1000 km\n• Battery check: Every 6 months\n• Book via OLA app or visit nearest service center",
      "📅 **Ather 450X Service Schedule:**\n• First service: 1000 km\n• Regular service: Every 1500 km\n• Battery health check: Every 6 months\n• AtherSpace centers in major cities",
      "📅 **TVS iQube Service Schedule:**\n• First service: 500 km\n• Regular service: Every 1000 km\n• Available at TVS dealerships nationwide",
      "📅 **Bajaj Chetak Service Schedule:**\n• First service: 1000 km\n• Regular service: Every 1200 km\n• Service at authorized Bajaj dealerships",
      "🔧 **General Service Checklist:**\n• Battery health check\n• Brake inspection\n• Tire pressure check\n• Motor diagnostics\n• Software updates\n• Cleaning and lubrication"
    ]
  },
  rides: {
    keywords: ["ride", "book", "booking", "start", "end", "trip", "journey", "unlock", "lock"],
    responses: [
      "To start a ride, scan the QR code on the scooter and follow the app instructions.",
      "Always wear a helmet and follow traffic rules when riding your electric scooter.",
      "End your ride by parking in designated areas and locking the scooter through the app.",
      "If you face issues starting a ride, check your app permissions and internet connection."
    ]
  },
  payment: {
    keywords: ["payment", "money", "bill", "cost", "price", "refund", "wallet", "card", "pay"],
    responses: [
      "Payment is processed automatically after each ride based on time and distance.",
      "You can add money to your wallet or link a credit/debit card for seamless payments.",
      "For refund requests, contact our support team with your trip ID within 24 hours.",
      "Check your trip history in the app to view detailed payment breakdowns."
    ]
  },
  maintenance: {
    keywords: ["repair", "service", "broken", "fix", "maintenance", "issue", "problem", "defect"],
    responses: [
      "Report damaged scooters immediately through the app to ensure safety for all users.",
      "Regular maintenance includes checking tire pressure, brakes, and battery connections.",
      "If you encounter a mechanical issue during a ride, end the trip safely and report it.",
      "Our service team conducts regular inspections and maintenance on all scooters."
    ]
  },
  safety: {
    keywords: ["safety", "helmet", "accident", "emergency", "rules", "traffic", "speed"],
    responses: [
      "Always wear a helmet and protective gear when riding an electric scooter.",
      "Follow local traffic laws and ride in designated areas only.",
      "Maximum speed is limited to 25 km/h for safety. Avoid riding in bad weather.",
      "In case of emergency, contact local authorities first, then report through our app."
    ]
  },
  account: {
    keywords: ["account", "profile", "login", "password", "phone", "verification", "register"],
    responses: [
      "Create your account using your phone number and complete OTP verification.",
      "Keep your profile information updated for better service and security.",
      "If you forgot your password, use the 'Forgot Password' option on the login screen.",
      "For account security, don't share your login credentials with others."
    ]
  }
};

interface KnowledgeItem {
  keywords: string[];
  responses: string[];
}

interface Knowledge {
  [key: string]: KnowledgeItem;
}

const AdminKnowledge = () => {
  const [knowledge, setKnowledge] = useState<Knowledge>({});
  const [editingCategory, setEditingCategory] = useState<string | null>(null);
  const [editingResponse, setEditingResponse] = useState<{ category: string; index: number } | null>(null);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newKeywords, setNewKeywords] = useState("");
  const [newResponse, setNewResponse] = useState("");
  const [isAddingCategory, setIsAddingCategory] = useState(false);
  const [isAddingResponse, setIsAddingResponse] = useState<string | null>(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Load knowledge from localStorage or use default
  useEffect(() => {
    const savedKnowledge = localStorage.getItem('adminKnowledge');
    if (savedKnowledge) {
      setKnowledge(JSON.parse(savedKnowledge));
    } else {
      setKnowledge(DEFAULT_KNOWLEDGE);
      localStorage.setItem('adminKnowledge', JSON.stringify(DEFAULT_KNOWLEDGE));
    }
  }, []);

  // Save knowledge to localStorage
  const saveKnowledge = (updatedKnowledge: Knowledge) => {
    setKnowledge(updatedKnowledge);
    localStorage.setItem('adminKnowledge', JSON.stringify(updatedKnowledge));
    toast({
      title: "Knowledge Updated",
      description: "Changes have been saved successfully.",
    });
  };

  // Add new category
  const addCategory = () => {
    if (!newCategoryName || !newKeywords) {
      toast({
        title: "Error",
        description: "Please provide both category name and keywords.",
        variant: "destructive",
      });
      return;
    }

    const updatedKnowledge = {
      ...knowledge,
      [newCategoryName.toLowerCase()]: {
        keywords: newKeywords.split(',').map(k => k.trim()),
        responses: []
      }
    };

    saveKnowledge(updatedKnowledge);
    setNewCategoryName("");
    setNewKeywords("");
    setIsAddingCategory(false);
  };

  // Delete category
  const deleteCategory = (categoryKey: string) => {
    const updatedKnowledge = { ...knowledge };
    delete updatedKnowledge[categoryKey];
    saveKnowledge(updatedKnowledge);
  };

  // Update keywords for a category
  const updateKeywords = (categoryKey: string, keywords: string[]) => {
    const updatedKnowledge = {
      ...knowledge,
      [categoryKey]: {
        ...knowledge[categoryKey],
        keywords
      }
    };
    saveKnowledge(updatedKnowledge);
  };

  // Add response to category
  const addResponse = (categoryKey: string) => {
    if (!newResponse) {
      toast({
        title: "Error",
        description: "Please provide a response text.",
        variant: "destructive",
      });
      return;
    }

    const updatedKnowledge = {
      ...knowledge,
      [categoryKey]: {
        ...knowledge[categoryKey],
        responses: [...knowledge[categoryKey].responses, newResponse]
      }
    };

    saveKnowledge(updatedKnowledge);
    setNewResponse("");
    setIsAddingResponse(null);
  };

  // Update response
  const updateResponse = (categoryKey: string, responseIndex: number, newText: string) => {
    const updatedKnowledge = {
      ...knowledge,
      [categoryKey]: {
        ...knowledge[categoryKey],
        responses: knowledge[categoryKey].responses.map((response, index) =>
          index === responseIndex ? newText : response
        )
      }
    };

    saveKnowledge(updatedKnowledge);
    setEditingResponse(null);
  };

  // Delete response
  const deleteResponse = (categoryKey: string, responseIndex: number) => {
    const updatedKnowledge = {
      ...knowledge,
      [categoryKey]: {
        ...knowledge[categoryKey],
        responses: knowledge[categoryKey].responses.filter((_, index) => index !== responseIndex)
      }
    };

    saveKnowledge(updatedKnowledge);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Knowledge Management</h1>
              <p className="text-muted-foreground">Manage questions and answers for the electric scooter chatbot</p>
            </div>
          </div>
          
          <Dialog open={isAddingCategory} onOpenChange={setIsAddingCategory}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Add Category
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Category</DialogTitle>
                <DialogDescription>
                  Create a new knowledge category with keywords and responses.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="categoryName">Category Name</Label>
                  <Input
                    id="categoryName"
                    value={newCategoryName}
                    onChange={(e) => setNewCategoryName(e.target.value)}
                    placeholder="e.g., battery, charging"
                  />
                </div>
                <div>
                  <Label htmlFor="keywords">Keywords (comma-separated)</Label>
                  <Input
                    id="keywords"
                    value={newKeywords}
                    onChange={(e) => setNewKeywords(e.target.value)}
                    placeholder="e.g., battery, charge, power, voltage"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsAddingCategory(false)}>
                    Cancel
                  </Button>
                  <Button onClick={addCategory}>
                    Add Category
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Knowledge Categories */}
        <div className="grid gap-6">
          {Object.entries(knowledge).map(([categoryKey, categoryData]) => (
            <Card key={categoryKey}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="capitalize">{categoryKey}</CardTitle>
                    <CardDescription>
                      {categoryData.responses.length} response(s) available
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditingCategory(editingCategory === categoryKey ? null : categoryKey)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteCategory(categoryKey)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Keywords Section */}
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Tags className="h-4 w-4" />
                    <Label className="text-sm font-medium">Keywords</Label>
                  </div>
                  {editingCategory === categoryKey ? (
                    <div className="flex gap-2">
                      <Input
                        value={categoryData.keywords.join(', ')}
                        onChange={(e) => {
                          const keywords = e.target.value.split(',').map(k => k.trim());
                          updateKeywords(categoryKey, keywords);
                        }}
                        placeholder="Enter keywords separated by commas"
                      />
                      <Button
                        size="sm"
                        onClick={() => setEditingCategory(null)}
                      >
                        <Save className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {categoryData.keywords.map((keyword, index) => (
                        <Badge key={index} variant="secondary">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {/* Responses Section */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label className="text-sm font-medium">Responses</Label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsAddingResponse(isAddingResponse === categoryKey ? null : categoryKey)}
                      className="flex items-center gap-2"
                    >
                      <Plus className="h-4 w-4" />
                      Add Response
                    </Button>
                  </div>

                  {/* Add New Response */}
                  {isAddingResponse === categoryKey && (
                    <div className="mb-4 p-4 border rounded-lg bg-muted/20">
                      <Label className="text-sm font-medium mb-2 block">New Response</Label>
                      <Textarea
                        value={newResponse}
                        onChange={(e) => setNewResponse(e.target.value)}
                        placeholder="Enter the response text..."
                        rows={4}
                        className="mb-2"
                      />
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setIsAddingResponse(null);
                            setNewResponse("");
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => addResponse(categoryKey)}
                        >
                          <Save className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Existing Responses */}
                  <div className="space-y-3">
                    {categoryData.responses.map((response, responseIndex) => (
                      <div key={responseIndex} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start gap-2">
                          <div className="flex-1">
                            {editingResponse?.category === categoryKey && editingResponse?.index === responseIndex ? (
                              <div>
                                <Textarea
                                  defaultValue={response}
                                  onBlur={(e) => updateResponse(categoryKey, responseIndex, e.target.value)}
                                  rows={4}
                                  className="mb-2"
                                />
                                <div className="flex justify-end gap-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setEditingResponse(null)}
                                  >
                                    <X className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>
                            ) : (
                              <div className="whitespace-pre-wrap text-sm">{response}</div>
                            )}
                          </div>
                          {!editingResponse && (
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setEditingResponse({ category: categoryKey, index: responseIndex })}
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => deleteResponse(categoryKey, responseIndex)}
                                className="text-destructive hover:text-destructive"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {Object.keys(knowledge).length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <h3 className="text-lg font-semibold mb-2">No Knowledge Categories</h3>
              <p className="text-muted-foreground mb-4">Add your first category to get started.</p>
              <Button onClick={() => setIsAddingCategory(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Category
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AdminKnowledge;
