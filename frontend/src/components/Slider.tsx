import { useState } from "react"
import { Range } from "react-range"

export default function Slider({
  min = 4,
  max = 40,
  step = 1,
  defaultValues = [6, 20],
  onChange,
}: {
  min?: number
  max?: number
  step?: number
  defaultValues?: [number, number]
  onChange: (v: [number, number]) => void
}) {
  const [values, setValues] = useState<[number, number]>(defaultValues)
  const [touched, setTouched] = useState(false)

  const handleSelect = () => {
    if (values[0] !== values[1]) {
      onChange(values)
    }
  }

  return (
    <div className="w-full px-2 py-6">
      <div className="text-sm text-gray-700 text-center mb-2">
        {values[0]}평 ~ {values[1]}평
      </div>
      <Range
        step={step}
        min={min}
        max={max}
        values={values}
        onChange={(vals: number[]) => {
          setTouched(true)
          setValues(vals as [number, number])
        }}
        renderTrack={({
          props,
          children,
        }: {
          props: React.HTMLAttributes<HTMLDivElement>
          children: React.ReactNode
        }) => (
          <div
            {...props}
            style={{
              ...props.style,
              height: "6px",
              width: "100%",
              backgroundColor: "#d1d5db",
              borderRadius: "4px",
            }}
          >
            {children}
          </div>
        )}
        renderThumb={({
          props,
        }: {
          props: React.HTMLAttributes<HTMLDivElement>
        }) => (
          <div
            {...props}
            style={{
              height: "20px",
              width: "20px",
              backgroundColor: "#433CFF",
              borderRadius: "50%",
            }}
          />
        )}
      />
      <div className="text-center mt-4">
        <button
          onClick={handleSelect}
          disabled={!touched || values[0] === values[1]}
          className={`py-2 px-4 rounded-full font-bold transition ${
            !touched || values[0] === values[1]
              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          선택 완료 →
        </button>
      </div>
    </div>
  )
}