import { useState, useMemo } from "react";
import {
  useTable,
  useGlobalFilter,
  useAsyncDebounce,
  useFilters,
} from "react-table";
import { Table, TextInput, Select, MultiSelect } from "@mantine/core";

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
    <TextInput
      placeholder={`Rummage through ${count} records`}
      label="Search"
      onChange={(e) => {
        setValue(e.target.value);
        onChange(e.target.value);
      }}
    />
  );
}

// This is a custom filter UI for selecting
// a unique option from a list
export function SelectColumnFilter({
  column: { filterValue, setFilter, preFilteredRows = [], id },
}) {
  // Calculate the options for filtering
  // using the preFilteredRows
  const options = useMemo(() => {
    const options = new Set();
    preFilteredRows.forEach((row) => {
      options.add(row.values[id]);
    });
    return [...options.values()];
  }, [id, preFilteredRows]);

  return (
    <Select
      label="Type"
      placeHolder="Filter through three question types"
      value={filterValue}
      onChange={(e) => {
        setFilter(e || undefined);
      }}
      data={options}
    />
  );
}

export default function ReactTable({ columns, data }) {
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
    useFilters, // useFilter is applied first
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
      {headerGroups.map((headerGroup) =>
        headerGroup.headers.map((column) =>
          column.Filter ? (
            <div key={column.id}>{column.render("Filter")}</div>
          ) : null
        )
      )}
      <Table
        {...getTableProps()}
        horizontalSpacing="xl"
        verticalSpacing="xs"
        fontSize="xs"
      >
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
      </Table>
      <div>
        <pre>
          <code>{JSON.stringify(state, null, 2)}</code>
        </pre>
      </div>
    </>
  );
}
