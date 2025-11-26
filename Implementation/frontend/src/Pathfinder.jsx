import React, { useState } from "react";

export default function Pathfinder() {
  const [results, setResults] = useState(null);
  const [interests, setInterests] = useState([]);
  const [skills, setSkills] = useState([]);
  const [currentInterest, setCurrentInterest] = useState("");
  const [currentSkill, setCurrentSkill] = useState("");
  const [education, setEducation] = useState("");
  const [gpa, setGpa] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [personality, setPersonality] = useState(Array(25).fill(0));
  const [personalityResult, setPersonalityResult] = useState(null);


  const personalityQuestions = [
  // Extraversion
  "I am the life of the party.",
  "I feel comfortable around people.",
  "I start conversations.",
  "I talk to a lot of different people at parties.",
  "I am quiet around strangers.",

  // Neuroticism
  "I get stressed out easily.",
  "I am relaxed most of the time.",
  "I worry about things.",
  "I get upset easily.",
  "I often feel blue.",

  // Agreeableness
  "I am interested in people.",
  "I sympathize with others’ feelings.",
  "I have a soft heart.",
  "I take time out for others.",
  "I feel little concern for others.",

  // Conscientiousness
  "I am always prepared.",
  "I pay attention to details.",
  "I get chores done right away.",
  "I like order.",
  "I shirk my duties.",

  // Openness
  "I have a rich vocabulary.",
  "I have a vivid imagination.",
  "I have excellent ideas.",
  "I am quick to understand things.",
  "I am full of ideas."
];


  // Compute O, C, E, A, N scores from 25 personality items (0–5 scale)
  const computeOceanFromAnswers = (answers) => {
    const get = (i) => Number(answers[i]);
    const reverse = (v) => 5 - Number(v); // reverse-scored items on 0–5 scale

    const mean = (arr) =>
      arr.reduce((sum, v) => sum + Number(v), 0) / (arr.length || 1);

    // Extraversion: Q1–Q5 (index 0–4), Q5 is reverse-scored
    const eItems = [get(0), get(1), get(2), get(3), reverse(get(4))];

    // Neuroticism: Q6–Q10 (index 5–9), Q7 is reverse-scored
    const nItems = [get(5), reverse(get(6)), get(7), get(8), get(9)];

    // Agreeableness: Q11–Q15 (index 10–14), Q15 is reverse-scored
    const aItems = [get(10), get(11), get(12), get(13), reverse(get(14))];

    // Conscientiousness: Q16–Q20 (index 15–19), Q20 is reverse-scored
    const cItems = [get(15), get(16), get(17), get(18), reverse(get(19))];

    // Openness: Q21–Q25 (index 20–24), all normal
    const oItems = [get(20), get(21), get(22), get(23), get(24)];

    const rawO = mean(oItems);
    const rawC = mean(cItems);
    const rawE = mean(eItems);
    const rawA = mean(aItems);
    const rawN = mean(nItems);

    // Map 0–5 scale to 1–5 scale expected by backend
    const toOneToFive = (v) => 1 + (v / 5) * 4;

    return {
      O: toOneToFive(rawO),
      C: toOneToFive(rawC),
      E: toOneToFive(rawE),
      A: toOneToFive(rawA),
      N: toOneToFive(rawN),
    };
  };


  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!education || !gpa || interests.length === 0 || skills.length === 0) {
      setError("Please fill out all required fields before submitting.");
      return;
    }

    setLoading(true);
    setError(null);

    // ---- 1) Career prediction payload ----
    const profilePayload = {
      education: education,
      gpa: parseFloat(gpa),
      interests: interests,
      skills: skills,
    };

    // ---- 2) Personality(OCEAN) calculation ----
    const oceanPayload = computeOceanFromAnswers(personality);
    // oceanPayload = { O: ..., C: ..., E: ..., A: ..., N: ... }

    try {
      // call APIs(Promise.all)
      const [personalityRes, careerRes] = await Promise.all([
        fetch("http://127.0.0.1:8000/personality", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(oceanPayload),
        }),
        fetch("http://127.0.0.1:8000/predict", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(profilePayload),
        }),
      ]);

      if (!personalityRes.ok) {
        throw new Error(
          `Personality HTTP error! Status: ${personalityRes.status}`
        );
      }
      if (!careerRes.ok) {
        throw new Error(`Career HTTP error! Status: ${careerRes.status}`);
      }

      const personalityData = await personalityRes.json();
      const careerData = await careerRes.json();

      // saving personality result
      setPersonalityResult(personalityData);

      // career result format
      const formattedResults = {
        careers: careerData.predictions.map((p) => p.job_category),
        courses: careerData.predictions.map((p) =>
          p.recommended_courses.join(", ")
        ),
        tips:
          "Results are generated based on your inputs and the backend model predictions.",
      };

      setResults(formattedResults);
    } catch (err) {
      console.error("Error fetching predictions:", err);
      setError(
        "Failed to fetch recommendations. Please check your backend server."
      );
    } finally {
      setLoading(false);
    }
  };

  

  // Add & remove interests
  const addInterest = (e) => {
    e.preventDefault();
    if (currentInterest.trim() && !interests.includes(currentInterest.trim())) {
      setInterests([...interests, currentInterest.trim()]);
      setCurrentInterest("");
    }
  };
  const removeInterest = (i) => setInterests(interests.filter((x) => x !== i));

  // Add & remove skills
  const addSkill = (e) => {
    e.preventDefault();
    if (currentSkill.trim() && !skills.includes(currentSkill.trim())) {
      setSkills([...skills, currentSkill.trim()]);
      setCurrentSkill("");
    }
  };
  const removeSkill = (s) => setSkills(skills.filter((x) => x !== s));

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
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

      <main className="container mx-auto px-6 py-12">
        <div className="max-w-6xl mx-auto">
          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-2xl shadow-xl border border-blue-100 overflow-hidden mb-12"
          >
            <div className="p-8 md:p-12">
              <section className="mb-12">
                <div className="flex items-center mb-8">
                  <div className="w-2 h-8 bg-blue-600 rounded-full mr-4"></div>
                  <h2 className="text-3xl font-bold text-gray-800">
                    Student Information
                  </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Education */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Degree or Diploma
                    </label>
                    <input
                      type="text"
                      value={education}
                      onChange={(e) => setEducation(e.target.value)}
                      placeholder="e.g., Computer Science"
                      className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    />
                  </div>

                  {/* GPA */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      GPA
                    </label>
                    <input
                      type="number"
                      value={gpa}
                      onChange={(e) => setGpa(e.target.value)}
                      placeholder="e.g., 3.8"
                      step="0.1"
                      min="0"
                      max="4.0"
                      className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    />
                  </div>

                  {/* Interests */}
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700">
                      Interests
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={currentInterest}
                        onChange={(e) => setCurrentInterest(e.target.value)}
                        placeholder="e.g., data analysis, cybersecurity, marketing"
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
                      <div className="mt-3 flex flex-wrap gap-2">
                        {interests.map((i, idx) => (
                          <div
                            key={idx}
                            className="bg-blue-100 text-blue-700 px-3 py-2 rounded-lg flex items-center gap-2"
                          >
                            <span>{i}</span>
                            <button
                              type="button"
                              onClick={() => removeInterest(i)}
                              className="text-blue-500 hover:text-blue-700 text-lg font-bold"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Skills */}
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700">
                      Skills
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={currentSkill}
                        onChange={(e) => setCurrentSkill(e.target.value)}
                        placeholder="e.g., Python, JavaScript, SQL"
                        className="flex-1 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                      />
                      <button
                        onClick={addSkill}
                        className="bg-green-500 text-white px-6 py-4 rounded-xl hover:bg-green-600 transition-all duration-200 font-medium"
                      >
                        Add
                      </button>
                    </div>

                    {skills.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {skills.map((s, idx) => (
                          <div
                            key={idx}
                            className="bg-green-100 text-green-700 px-3 py-2 rounded-lg flex items-center gap-2"
                          >
                            <span>{s}</span>
                            <button
                              type="button"
                              onClick={() => removeSkill(s)}
                              className="text-green-500 hover:text-green-700 text-lg font-bold"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                {/* Personality Questions */}
                <div className="space-y-6 md:col-span-2 mt-10">
                  <div className="flex items-center mb-6">
                    <div className="w-2 h-8 bg-blue-600 rounded-full mr-4"></div>
                    <h2 className="text-2xl font-bold text-gray-800">
                      Personality Assessment
                    </h2>
                  </div>

                  <p className="text-gray-600 mb-4">
                    Rate each statement from <strong>1 (Strongly Disagree)</strong> to{" "}
                    <strong>5 (Strongly Agree)</strong>.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {personalityQuestions.map((question, index) => (
                      <div
                        key={index}
                        className="bg-gray-50 border border-gray-200 p-4 rounded-xl shadow-sm hover:shadow-md transition-all"
                      >
                        <label className="block text-gray-800 font-medium mb-2">
                          {index + 1}. {question}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="5"
                          step="1"
                          value={personality[index]}
                          onChange={(e) => {
                            const updated = [...personality];
                            updated[index] = parseInt(e.target.value);// change to integer
                            setPersonality(updated);
                          }}
                          className="w-full accent-blue-600"
                        />
                        <div className="text-right text-sm text-gray-600">
                          {personality[index]}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </section>

              {/* Submit */}
              <div className="flex justify-center pt-6">
                <button
                  type="submit"
                  disabled={loading}
                  className={`${
                    loading
                      ? "bg-gray-400 cursor-not-allowed"
                      : "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  } text-white px-12 py-4 rounded-xl font-semibold text-lg transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl`}
                >
                  {loading ? "Loading..." : "Get Recommendations"}
                </button>
              </div>

              {error && (
                <p className="text-center text-red-600 mt-4 font-medium">{error}</p>
              )}
            </div>
          </form>

      {/* Personality Result */}
          {personalityResult && (
            <div className="bg-white rounded-2xl shadow-xl border border-purple-200 overflow-hidden mb-10">
              <div className="p-8 md:p-12">
                <h2 className="text-3xl font-bold text-gray-800 mb-3">
                  Your Personality Profile
                </h2>
                <p className="text-xl font-semibold text-purple-700 mb-3">
                  {personalityResult.cluster_name}
                </p>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {personalityResult.description_en}
                </p>
              </div>
            </div>
          )}

          {/* Display Results */}
          {results && (
            <div className="bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-xl border border-blue-200 overflow-hidden">
              <div className="p-8 md:p-12">
                <h2 className="text-3xl font-bold text-gray-800 mb-8">
                  Your Career Recommendations
                </h2>

                {results.careers.map((career, index) => (
                  <div
                    key={index}
                    className="bg-white border border-gray-200 rounded-xl p-6 mb-4 hover:shadow-md transition-shadow duration-200"
                  >
                    <h4 className="text-lg font-bold text-blue-700 mb-2">
                      {career}
                    </h4>
                    <p className="text-gray-600">
                      <span className="font-medium">Recommended Courses:</span>{" "}
                      {results.courses[index]}
                    </p>
                  </div>
                ))}

                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mt-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">
                    Personalized Advice
                  </h3>
                  <p className="text-gray-700">{results.tips}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
