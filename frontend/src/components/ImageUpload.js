import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, FileImage, Brain, Heart, Eye } from 'lucide-react';

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisType, setAnalysisType] = useState('emotion');
  const fileInputRef = useRef(null);

  const analysisTypes = [
    { id: 'emotion', label: 'Emotion Analysis', icon: Brain, endpoint: '/api/analyze/image' },
    { id: 'lie', label: 'Lie Detection', icon: Eye, endpoint: '/api/analyze/lie-detection' },
    { id: 'stress', label: 'Stress Analysis', icon: Heart, endpoint: '/api/analyze/stress' }
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setAnalysis(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const selectedAnalysis = analysisTypes.find(type => type.id === analysisType);
      const response = await axios.post(selectedAnalysis.endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setAnalysis(response.data);
    } catch (error) {
      console.error('Analysis failed:', error);
      setAnalysis({
        success: false,
        error: 'Analysis failed. Please try again.'
      });
    }

    setIsLoading(false);
  };

  const renderAnalysisResult = () => {
    if (!analysis) return null;

    if (!analysis.success) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{analysis.error || 'Analysis failed'}</p>
        </div>
      );
    }

    switch (analysisType) {
      case 'emotion':
        return (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">Emotion Analysis Results</h3>
            {analysis.analysis && (
              <div className="space-y-2">
                <p><strong>Main Emotion:</strong> {analysis.analysis.emotional_state}</p>
                <p><strong>Confidence:</strong> {analysis.analysis.confidence_level}</p>
                {analysis.analysis.facial_expressions && (
                  <p><strong>Expressions:</strong> {analysis.analysis.facial_expressions.join(', ')}</p>
                )}
                {analysis.analysis.detailed_analysis && (
                  <div>
                    <strong>Detailed Analysis:</strong>
                    <p className="mt-1 text-gray-700">{analysis.analysis.detailed_analysis}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        );

      case 'lie':
        return (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">Lie Detection Results</h3>
            {analysis.deception_analysis && (
              <div className="space-y-2">
                <p><strong>Deception Probability:</strong> {(analysis.deception_analysis.deception_probability * 100).toFixed(1)}%</p>
                <p><strong>Confidence Level:</strong> {analysis.deception_analysis.confidence_level}</p>
                {analysis.deception_analysis.key_indicators && (
                  <div>
                    <strong>Key Indicators:</strong>
                    <ul className="mt-1 list-disc list-inside">
                      {analysis.deception_analysis.key_indicators.map((indicator, index) => (
                        <li key={index} className="text-gray-700">{indicator}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {analysis.deception_analysis.ai_interpretation && (
                  <div>
                    <strong>AI Interpretation:</strong>
                    <p className="mt-1 text-gray-700">{analysis.deception_analysis.ai_interpretation}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        );

      case 'stress':
        return (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">Stress Analysis Results</h3>
            {analysis.stress_analysis && (
              <div className="space-y-2">
                <p><strong>Stress Level:</strong> {analysis.stress_analysis.stress_percentage}% ({analysis.stress_analysis.stress_level})</p>
                {analysis.stress_analysis.indicators && (
                  <div>
                    <strong>Stress Indicators:</strong>
                    <ul className="mt-1 list-disc list-inside">
                      {analysis.stress_analysis.indicators.map((indicator, index) => (
                        <li key={index} className="text-gray-700">{indicator.replace('_', ' ')}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {analysis.stress_analysis.recommendations && (
                  <div>
                    <strong>Recommendations:</strong>
                    <ul className="mt-1 list-disc list-inside">
                      {analysis.stress_analysis.recommendations.map((rec, index) => (
                        <li key={index} className="text-gray-700">{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Upload & Analyze</h1>
        <p className="text-gray-600">Upload an image for AI-powered emotion analysis</p>
      </div>

      {/* Analysis Type Selection */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Select Analysis Type</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {analysisTypes.map((type) => {
            const Icon = type.icon;
            return (
              <button
                key={type.id}
                onClick={() => setAnalysisType(type.id)}
                className={`p-4 rounded-lg border-2 transition-colors ${
                  analysisType === type.id
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon size={24} className="mx-auto mb-2" />
                <p className="font-medium">{type.label}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* File Upload */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
        >
          <Upload size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-lg font-medium mb-2">
            {selectedFile ? selectedFile.name : 'Click to upload an image'}
          </p>
          <p className="text-gray-500">
            Supports JPG, PNG files up to 10MB
          </p>
        </div>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="image/*"
          className="hidden"
        />

        {selectedFile && (
          <div className="mt-4 flex justify-center">
            <img
              src={URL.createObjectURL(selectedFile)}
              alt="Selected"
              className="max-w-xs max-h-64 rounded-lg shadow-md"
            />
          </div>
        )}

        {selectedFile && (
          <div className="mt-4 text-center">
            <button
              onClick={handleAnalyze}
              disabled={isLoading}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Analyzing...</span>
                </div>
              ) : (
                `Analyze ${analysisTypes.find(t => t.id === analysisType)?.label}`
              )}
            </button>
          </div>
        )}
      </div>

      {/* Analysis Results */}
      {renderAnalysisResult()}
    </div>
  );
};

export default ImageUpload;