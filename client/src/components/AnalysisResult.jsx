import React from "react";

const AnalysisResult = ({ data }) => {
  if (!Array.isArray(data) || data.length === 0) {
    return <p className="text-gray-500 text-sm">Gösterilecek analiz sonucu yok.</p>;
  }

  return (
    <div className="space-y-4">
      {data.map((item, index) => (
        <div
          key={index}
          className="p-4 bg-gray-800 rounded-lg shadow flex flex-col gap-1"
        >
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-semibold text-white">{item?.indikator || "—"}</h3>
            <span
              className={`text-sm font-bold ${item?.sinyal === "YUKARI"
                  ? "text-green-400"
                  : item?.sinyal === "AŞAĞI"
                    ? "text-red-400"
                    : "text-gray-400"
                }`}
            >
              {item?.sinyal || "YOK"}
            </span>
          </div>
          {Array.isArray(item?.sebepler) && item.sebepler.length > 0 && (
            <ul className="list-disc list-inside text-xs text-gray-300 mt-1 space-y-1">
              {item.sebepler.map((sebep, i) => (
                <li key={i}>{sebep}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
};

export default AnalysisResult;