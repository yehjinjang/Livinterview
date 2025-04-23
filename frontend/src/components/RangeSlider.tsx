import { Range, getTrackBackground } from "react-range"

interface Props {
  label: string
  min: number
  max: number
  step: number
  unit: string
  value: [number, number]
  onChange: (val: [number, number]) => void
}

export default function RangeSlider({
  label,
  min,
  max,
  step,
  unit,
  value,
  onChange,
}: Props) {
  return (
    <div>
      <p className="text-sm font-semibold mb-1">{label}</p>
      <div className="flex items-center justify-between text-xs mb-1">
        <span>{value[0]}{unit}</span>
        <span>{value[1]}{unit}</span>
      </div>
      <Range
        values={value}
        step={step}
        min={min}
        max={max}
        onChange={(vals) => onChange([vals[0], vals[1]])}
        renderTrack={({ props, children }) => (
          <div
            {...props}
            style={{
              height: "6px",
              width: "100%",
              background: getTrackBackground({
                values: value,
                colors: ["#ccc", "#3b82f6", "#ccc"],
                min,
                max,
              }),
              borderRadius: "4px",
              marginTop: "8px",
            }}
          >
            {children}
          </div>
        )}
        renderThumb={({ props }) => (
          <div
            {...props}
            style={{
              height: "20px",
              width: "20px",
              borderRadius: "10px",
              backgroundColor: "#3b82f6",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              boxShadow: "0 0 0 1px white",
            }}
          />
        )}
      />
    </div>
  )
}
