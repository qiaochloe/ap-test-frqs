import ReactTable, { SelectColumnFilter } from "../components/ReactTable";
import { useMemo } from "react";
import { getData } from "../data/apwh";

export default function Demo() {
  const columns = useMemo(
    () => [
      {
        Header: "Question",
        accessor: "question",
      },
      {
        Header: "Type",
        accessor: "question_type",
        Filter: SelectColumnFilter,
        filter: "includes",
      },
      {
        Header: "Number",
        accessor: "question_number",
      },
      {
        Header: "Year",
        accessor: "year",
      },
    ],
    []
  );

  const data = useMemo(() => getData(), []);

  return (
    <>
      <h1>Hello React!</h1>
      <div>
        <ReactTable columns={columns} data={data} />
      </div>
    </>
  );
}
