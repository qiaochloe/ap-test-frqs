import { useState } from "react";
import { useTable, useGlobalFilter, useAsyncDebounce } from "react-table";

// the useAsyncDeBounch creates a ReferenceError: regeneratorRuntime is not defined if this is not here
// see https://github.com/TanStack/table/issues/2071
import "regenerator-runtime/runtime";

// Define a default UI for filtering
function GlobalFilter({
  // props provided by Table component
  preGlobalFilteredRows,
  globalFilter,
  setGlobalFilter,
}) {
  const count = preGlobalFilteredRows.length;

  // When the user types in the <input> element, the `onChange` handler
  // calls the `setGlobalFilter` method to pass `value` to the parent `Table`
  // `useAsyncDebounce` is to add some delay
  const [value, setValue] = useState(globalFilter);
  const onChange = useAsyncDebounce((value) => {
    setGlobalFilter(value || undefined);
  }, 200);

  return (
    <span>
      Search:{" "}
      <input
        value={value || ""}
        onChange={(e) => {
          setValue(e.target.value);
          onChange(e.target.value);
        }}
        placeholder={`${count} records...`}
      />
    </span>
  );
}

export default function Table({ columns, data }) {
  // Use the state and functions returned from useTable to build the UI
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    state,
    preGlobalFilteredRows,
    setGlobalFilter,
  } = useTable(
    {
      columns,
      data,
    },
    useGlobalFilter
  );

  // render the UI for the table
  //<table>
  //  <thead>
  //  </thead>
  //  <tbody>
  //    <tr>
  //      <td>
  //      </td>
  //    </tr>
  //  </tbody>
  //</table>

  return (
    <>
      <GlobalFilter
        preGlobalFilteredRows={preGlobalFilteredRows}
        globalFilter={state.globalFilter}
        setGlobalFilter={setGlobalFilter}
      />
      <table {...getTableProps()} border="1">
        <thead>
          {headerGroups.map((headerGroup) => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <th {...column.getHeaderProps()}>{column.render("Header")}</th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row, i) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map((cell) => {
                  return (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}
