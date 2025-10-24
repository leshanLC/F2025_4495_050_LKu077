import React, { useState } from "react";

export default function Pathfinder() {
  const [results, setResults] = useState(null);
  const [interests, setInterests] = useState([]);
  const [skills, setSkills] = useState([]);
  const [currentInterest, setCurrentInterest] = useState("");
  const [currentSkill, setCurrentSkill] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // Demo mock results
    const mockResults = {
      careers: [
        "Data Analyst",
        "Software Engineer",
        "UX Designer",
        "Digital Marketer",
        "Project Manager",
      ],
      courses: [
        "Data Visualization, SQL for Analytics",
        "Advanced JavaScript, System Design",
        "UI/UX Tools, Human-Computer Interaction",
        "SEO, Google Ads Certification",
        "Agile Management, Leadership Skills",
      ],
      tips: "You show strong analytical and collaborative traits. Try engaging in data-driven team projects and leadership workshops to boost your professional edge.",
    };
    setResults(mockResults);
  };

  const addInterest = (e) => {
    e.preventDefault();
    if (currentInterest.trim() && !interests.includes(currentInterest.trim())) {
      setInterests([...interests, currentInterest.trim()]);
      setCurrentInterest("");
    }
  };

  const removeInterest = (interestToRemove) => {
    setInterests(interests.filter(interest => interest !== interestToRemove));
  };

  const addSkill = (e) => {
    e.preventDefault();
    if (currentSkill.trim() && !skills.includes(currentSkill.trim())) {
      setSkills([...skills, currentSkill.trim()]);
      setCurrentSkill("");
    }
  };

  const removeSkill = (skillToRemove) => {
    setSkills(skills.filter(skill => skill !== skillToRemove));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header Section */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 py-12 shadow-lg">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
            Pathfinder
          </h1>
          <p className="text-blue-100 text-xl font-light max-w-2xl mx-auto leading-relaxed">
            Personalized Career Path Recommender System for University Students
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Form Section */}
          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-2xl shadow-xl border border-blue-100 overflow-hidden mb-12"
          >
            <div className="p-8 md:p-12">
              {/* Student Information */}
              <section className="mb-12">
                <div className="flex items-center mb-8">
                  <div className="w-2 h-8 bg-blue-600 rounded-full mr-4"></div>
                  <h2 className="text-3xl font-bold text-gray-800">
                    Student Information
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Degree or Diploma
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Computer Science"
                      className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      GPA
                    </label>
                    <input
                      type="number"
                      placeholder="e.g., 3.8"
                      step="0.1"
                      min="0"
                      max="4.0"
                      className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    />
                  </div>
                  
                  {/* Interests List */}
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700">
                      Interests
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={currentInterest}
                        onChange={(e) => setCurrentInterest(e.target.value)}
                        placeholder="e.g., data analysis, cybersecurity, digital marketing"
                        className="flex-1 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                      />
                      <button
                        onClick={addInterest}
                        className="bg-blue-500 text-white px-6 py-4 rounded-xl hover:bg-blue-600 transition-all duration-200 font-medium"
                      >
                        Add
                      </button>
                    </div>
                    {interests.length > 0 && (
                      <div className="mt-3">
                        <div className="flex flex-wrap gap-2">
                          {interests.map((interest, index) => (
                            <div
                              key={index}
                              className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg flex items-center gap-2"
                            >
                              <span>{interest}</span>
                              <button
                                type="button"
                                onClick={() => removeInterest(interest)}
                                className="text-blue-500 hover:text-blue-700 text-lg font-bold"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Skills List */}
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700">
                      Skills
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={currentSkill}
                        onChange={(e) => setCurrentSkill(e.target.value)}
                        placeholder="e.g., Python, Excel, SQL, JavaScript, Project Management"
                        className="flex-1 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                      />
                      <button
                        onClick={addSkill}
                        className="bg-green-500 text-white px-6 py-4 rounded-xl hover:bg-green-600 transition-all duration-200 font-medium"
                      >
                        Add
                      </button>
                    </div>
                    {skills.length > 0 && (
                      <div className="mt-3">
                        <div className="flex flex-wrap gap-2">
                          {skills.map((skill, index) => (
                            <div
                              key={index}
                              className="bg-green-100 text-green-700 px-3 py-2 rounded-lg flex items-center gap-2"
                            >
                              <span>{skill}</span>
                              <button
                                type="button"
                                onClick={() => removeSkill(skill)}
                                className="text-green-500 hover:text-green-700 text-lg font-bold"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </section>

              {/* Personality Traits */}
              <section className="mb-12">
                <div className="flex items-center mb-8">
                  <div className="w-2 h-8 bg-indigo-600 rounded-full mr-4"></div>
                  <h2 className="text-3xl font-bold text-gray-800">
                    Personality & Work Preferences
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Preferred Work Style
                    </label>
                    <select className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                      <option>Select Work Style</option>
                      <option>Independently</option>
                      <option>In a team</option>
                      <option>Mix of both</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Problem Solving Style
                    </label>
                    <select className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                      <option>Select Problem Solving Style</option>
                      <option>Logical and structured</option>
                      <option>Creative and intuitive</option>
                      <option>Collaborative</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Leadership Preference
                    </label>
                    <select className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                      <option>Select Leadership Preference</option>
                      <option>Enjoy leading</option>
                      <option>Sometimes lead</option>
                      <option>Prefer supporting roles</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Risk Tolerance
                    </label>
                    <select className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                      <option>Select Risk Tolerance</option>
                      <option>Low</option>
                      <option>Moderate</option>
                      <option>High</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Detail Orientation
                    </label>
                    <select className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                      <option>Select Detail Orientation</option>
                      <option>Detail-focused</option>
                      <option>Big-picture thinker</option>
                      <option>Balanced</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Motivation Type
                    </label>
                    <select className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                      <option>Select Motivation Type</option>
                      <option>Achievement-driven</option>
                      <option>Learning-focused</option>
                      <option>Impact-oriented</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* Submit Button */}
              <div className="flex justify-center pt-6">
                <button
                  type="submit"
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-12 py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  Get Recommendations
                </button>
              </div>
            </div>
          </form>

          {/* Results Section */}
          {results && (
            <div className="bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-xl border border-blue-200 overflow-hidden">
              <div className="p-8 md:p-12">
                <div className="flex items-center mb-8">
                  <div className="w-2 h-8 bg-green-500 rounded-full mr-4"></div>
                  <h2 className="text-3xl font-bold text-gray-800">
                    Your Career Recommendations
                  </h2>
                </div>
                
                {/* Career List */}
                <div className="mb-10">
                  <h3 className="text-xl font-semibold text-gray-700 mb-6">
                    Recommended Career Paths
                  </h3>
                  <div className="space-y-4">
                    {results.careers.map((career, index) => (
                      <div
                        key={index}
                        className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow duration-200"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="text-lg font-bold text-blue-700 mb-2">
                              {career}
                            </h4>
                            <p className="text-gray-600">
                              <span className="font-medium">Recommended Courses:</span>{" "}
                              {results.courses[index]}
                            </p>
                          </div>
                          <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
                            {index + 1}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Tips Section */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-10">
                  <div className="flex items-center mb-3">
                    <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center mr-3">
                      <span className="text-white text-sm">💡</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800">
                      Personalized Advice
                    </h3>
                  </div>
                  <p className="text-gray-700 leading-relaxed">
                    {results.tips}
                  </p>
                </div>

                {/* Job Market Trend */}
                <div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-6">
                    Job Market Trends
                  </h3>
                  <div className="bg-white border border-gray-200 rounded-xl p-8">
                    <div className="h-64 flex items-center justify-center text-gray-400">
                      <div className="text-center">
                        <div className="text-4xl mb-4">📊</div>
                        <p className="text-lg font-medium">Market Trends Visualization</p>
                        <p className="text-sm text-gray-500 mt-2">
                          Interactive chart showing demand for your recommended careers
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}