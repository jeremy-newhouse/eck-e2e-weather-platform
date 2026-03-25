import SearchContainer from "@/components/search/SearchContainer";

export default function HomePage() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
        Search for a City
      </h1>
      <SearchContainer />
    </div>
  );
}
