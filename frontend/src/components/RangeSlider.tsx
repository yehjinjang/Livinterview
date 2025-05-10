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

// 금액 포맷팅 
function formatPrice(val: number) {
  if (val >= 10000) {
    const 억 = Math.floor(val / 10000)
    const 천 = val % 10000
    if (천 === 0) {
      return `${억}억`
    } else {
      return `${억}억 ${천}만`
    }
  }
  return `${val}만`
}

export default function RangeSlider({
  label,
  min,
  max,
  step,
  value,
  onChange,
}: Props) {
  const isValid = value.length === 2 && value[0] !== value[1] && value[0] >= min && value[1] <= max

  if (!isValid) {
    return null
  }

  const mid = Math.floor((min + max) / 2)

  return (
    <div className="space-y-2">
      {/* 라벨 및 값 범위 */}
      <div>
        <p className="text-sm font-semibold mb-4">{label}</p>
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

      {/* 중간값 라벨 추가 */}
      <div className="relative h-5">
        <span className="absolute left-0 text-xs text-gray-500">{formatPrice(min)}</span>
        <span className="absolute left-1/2 -translate-x-1/2 text-xs text-gray-500">{formatPrice(mid)}</span>
        <span className="absolute right-0 text-xs text-gray-500">{formatPrice(max)}</span>
      </div>
    </div>
  )
}