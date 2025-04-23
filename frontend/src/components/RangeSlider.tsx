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
    <div className="space-y-2">
      {/* 라벨 및 값 범위 */}
      <div>
        <p className="text-sm font-semibold">{label}</p>
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>{value[0]}{unit}</span>
          <span>{value[1]}{unit}</span>
        </div>
      </div>

      {/* 슬라이더 */}
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
              ...props.style,
              height: "6px",
              width: "100%",
              background: getTrackBackground({
                values: value,
                colors: ["#ccc", "#433CFF", "#ccc"],
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
        renderThumb={({ props, index }) => {
          const { key, ...rest } = props
          return (
            <div
              key={key}
              {...rest}
              style={{
                ...rest.style,
                height: "20px",
                width: "20px",
                borderRadius: "50%",
                backgroundColor: "#433CFF",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                transform: "translateY(-2px)",
                boxShadow: "0 0 0 1px white",
              }}
            >
              <span className="sr-only">{index === 0 ? "최소" : "최대"}</span>
            </div>
          )
        }}
      />
    </div>
  )
}