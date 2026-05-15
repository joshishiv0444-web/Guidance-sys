export default function TopBar({ title, subtitle }) {
  return (
    <div className="mb-8">
      <h1 className="text-2xl font-semibold text-white tracking-tight">{title}</h1>
      {subtitle && <p className="text-[14px] text-[#555] mt-1">{subtitle}</p>}
    </div>
  );
}
