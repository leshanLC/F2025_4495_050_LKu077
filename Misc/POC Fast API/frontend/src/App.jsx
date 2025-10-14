import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [formData, setFormData] = useState({
    cap_shape: "",
    cap_surface: "",
    cap_color: "",
    bruises: "",
    odor: "",
    gill_attachment: "",
    gill_spacing: "",
    gill_size: "",
    gill_color: "",
    stalk_shape: "",
    stalk_root: "",
    stalk_surface_above_ring: "",
    stalk_surface_below_ring: "",
    stalk_color_above_ring: "",
    stalk_color_below_ring: "",
    veil_type: "",
    veil_color: "",
    ring_number: "",
    ring_type: "",
    spore_print_color: "",
    population: "",
    habitat: "",
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);
    try {
      const response = await axios.post("http://127.0.0.1:8000/predict", formData);
      const result = response.data.prediction;
      setPrediction(result === "e" ? "Edible 🍄" : "Poisonous ☠️");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-6 text-center">
        🍄 Mushroom Edibility Predictor
      </h1>

      <form
        onSubmit={handleSubmit}
        className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white p-6 rounded-2xl shadow-md w-full max-w-3xl"
      >
        {Object.keys(formData).map((key) => (
          <div key={key} className="flex flex-col">
            <label className="font-semibold capitalize text-gray-800">{key.replace(/_/g, " ")}</label>
            <input
              type="text"
              name={key}
              value={formData[key]}
              onChange={handleChange}
              required
              className="border border-gray-300 rounded-md p-2"
            />
          </div>
        ))}

        <div className="col-span-full flex justify-center">
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg mt-4"
          >
            {loading ? "Predicting..." : "Predict"}
          </button>
        </div>
      </form>

      {prediction && (
        <div className="mt-6 text-xl font-semibold text-center">
          Result: <span className={prediction.includes("Edible") ? "text-green-600" : "text-red-600"}>{prediction}</span>
        </div>
      )}

      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
};

export default App;
