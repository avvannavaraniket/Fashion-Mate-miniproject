import { GoogleGenAI, Type } from "@google/genai";
import { StylistResponse } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const getOutfitRecommendation = async (
  occasion: string,
  gender: string,
  preferences?: string,
  imagePart?: { inlineData: { data: string; mimeType: string } }
): Promise<StylistResponse> => {
  const modelId = "gemini-2.5-flash"; // Best for fast text generation
  
  const systemInstruction = `
    You are a world-class AI Fashion Stylist. 
    Your goal is to recommend elegant, stylish, and appropriate outfits based on the user's event, gender identity, and optional visual input.
    
    PERSONALIZATION RULES:
    If preferences are provided, treat them as a User Style Profile. You must:
    1. **Prioritize**: Select items matching their favorite colors, preferred styles (e.g., Minimal, Y2K, Korean), and fits (baggy, regular).
    2. **Budget Alignment**: Respect any stated budget level (low/mid/high) by suggesting items that look the part.
    3. **Strict Restrictions**: ABSOLUTELY AVOID any disliked items or specific restrictions mentioned.
    4. **Cohesion**: Ensure the final look feels naturally aligned with the user's aesthetic. Do not force mismatches.
    
    OUTPUT GUIDELINES:
    - **Minimal yet Powerful**: Be concise. Use evocative language. Avoid filler words.
    - **Primary Outfit**: This must be the perfect marriage of the Occasion + User Profile.
    - **Reasoning**: Explain *why* this fits their specific profile and the event.
    - **Additional Suggestions**: Provide 3 distinct variations (e.g., "The Edgy Option", "The Comfort Choice") that still respect their core dislikes.
    
    If an image is provided:
    - Analyze it deeply.
    - If it's a clothing item: Make it the centerpiece.
    - If it's a mood/scene: Translate that vibe into clothing textures and colors.
  `;

  const userPrompt = `
    Curate an outfit for a ${gender}.
    Occasion: "${occasion}".
    User Style Profile / Preferences: "${preferences || "None provided"}"
    ${imagePart ? "Visual Context: An image has been provided. Analyze it and integrate it into the styling." : ""}
    
    Return a JSON response with the best possible outfit and suggestions.
  `;

  // Construct contents with text and optional image
  const contents = {
    parts: [
      { text: userPrompt },
      ...(imagePart ? [imagePart] : [])
    ]
  };

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: contents,
      config: {
        systemInstruction: systemInstruction,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            primary_outfit: {
              type: Type.OBJECT,
              properties: {
                title: { type: Type.STRING },
                top: { type: Type.STRING },
                bottom: { type: Type.STRING },
                footwear: { type: Type.STRING },
                accessories: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                },
                reasoning: { type: Type.STRING },
              },
              required: ["title", "top", "bottom", "footwear", "accessories", "reasoning"],
            },
            additional_suggestions: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  label: { type: Type.STRING },
                  outfit_summary: { type: Type.STRING },
                },
                required: ["label", "outfit_summary"],
              },
            },
            styling_notes: { type: Type.STRING },
          },
          required: ["primary_outfit", "additional_suggestions", "styling_notes"],
        },
      },
    });

    const text = response.text;
    if (!text) {
      throw new Error("No response received from AI Stylist.");
    }

    return JSON.parse(text) as StylistResponse;
  } catch (error) {
    console.error("Gemini API Error:", error);
    throw new Error("Unable to generate outfit recommendations at this time. Please try again.");
  }
};