import { useState } from "react"
import RangeSlider from "./RangeSlider"

interface FilterCardProps {
  onFilterChange: (filters: any) => void
}

export default function FilterCard({ onFilterChange }: FilterCardProps) {
  const [contractType, setContractType] = useState<"월세" | "전세">("월세")
  const [depositRange, setDepositRange] = useState<[number, number]>([0, 10000])
  const [monthlyRange, setMonthlyRange] = useState<[number, number]>([0, 500])
  const [sizeOption, setSizeOption] = useState<string>("전체")

  return (
    <div className="absolute top-4 left-4 bg-white rounded-xl shadow-lg p-4 w-[320px] z-50 space-y-5">
      {/* 계약 형태 */}
      <div>
        <p className="text-sm font-semibold">거래유형</p>
        <div className="flex gap-2 mt-2">
          {["월세", "전세"].map((type) => (
            <button
              key={type}
              onClick={() => setContractType(type as "월세" | "전세")}
              className={`px-3 py-1 rounded-full border text-sm transition ${
                contractType === type ? "bg-zipup-600 text-white" : "bg-white"
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* 면적 옵션 */}
      <div>
        <p className="text-sm font-semibold">면적 (평)</p>
        <select
          value={sizeOption}
          onChange={(e) => setSizeOption(e.target.value)}
          className="mt-2 w-full border rounded px-2 py-1 text-sm"
        >
          {["전체", "1~5", "5~10", "10~15", "15~20", "20 이상"].map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      {/* 조건별 슬라이더 */}
      {contractType === "월세" && (
        <>
          <RangeSlider
            label="보증금"
            min={0}
            max={10000}
            step={100}
            unit="만원"
            value={depositRange}
            onChange={setDepositRange}
          />
          <RangeSlider
            label="월세"
            min={0}
            max={500}
            step={10}
            unit="만원"
            value={monthlyRange}
            onChange={setMonthlyRange}
          />
        </>
      )}

      {contractType === "전세" && (
        <RangeSlider
          label="전세금"
          min={0}
          max={10000}
          step={100}
          unit="만원"
          value={depositRange}
          onChange={setDepositRange}
        />
      )}

      {/* 적용 버튼 */}
      <div className="flex justify-end pt-2">
        <button
          onClick={() =>
            onFilterChange({
              contractType,
              depositRange,
              monthlyRange,
              sizeOption,
            })
          }
          className="text-sm px-4 py-2 rounded-lg bg-zipup-600 text-white hover:bg-blue-700 transition"
        >
          적용
        </button>
      </div>
    </div>
  )
}