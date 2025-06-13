import React, { useEffect, useState } from "react";
import Select from "react-select";

const CoinSelector = ({ selectedExchange, onCoinChange, selectedCoin, coinList }) => {
  const [selectedOption, setSelectedOption] = useState(null);

  useEffect(() => {
    if (selectedCoin) {
      setSelectedOption({ value: selectedCoin, label: selectedCoin });
    } else if (coinList.length > 0) {
      const first = coinList[0];
      setSelectedOption({ value: first, label: first });
      onCoinChange(first);
    }
  }, [selectedCoin, coinList, onCoinChange]);

  const handleChange = (selected) => {
    setSelectedOption(selected);
    onCoinChange(selected?.value || "");
  };

  const options = coinList.map((coin) => ({
    value: coin,
    label: coin,
  }));

  return (
    <div style={{ minWidth: "250px" }}>
      <Select
        options={options}
        value={selectedOption}
        onChange={handleChange}
        placeholder="Coin seçin"
        isSearchable
        noOptionsMessage={() => "Coin bulunamadı"}
        loadingMessage={() => "Yükleniyor..."}
        styles={{
          control: (base, state) => ({
            ...base,
            backgroundColor: "#1F2937",
            borderColor: state.isFocused ? '#3B82F6' : "#374151",
            boxShadow: state.isFocused ? '0 0 0 1px #3B82F6' : 'none',
            '&:hover': { borderColor: '#4B5563' }
          }),
          menu: (base) => ({ ...base, backgroundColor: "#1F2937" }),
          option: (base, state) => ({
            ...base,
            backgroundColor: state.isSelected
              ? "#1E40AF"
              : state.isFocused
              ? "#3B82F6"
              : "#1F2937",
            color: "#fff",
          }),
          singleValue: (base) => ({ ...base, color: "#fff" }),
          placeholder: (base) => ({ ...base, color: "#9CA3AF" }),
          input: (base) => ({ ...base, color: "#ffffff" }) // ← bu çok kritik
        }}
        aria-label="Coin Seçimi"
      />
    </div>
  );
};

export default CoinSelector;
